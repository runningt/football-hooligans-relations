import csv
import os
from unittest.mock import MagicMock, patch

import pytest
from scrappers.stadionowioprawcy_net_scrapper import (fetch_club_links,
                                                      fetch_relations)


def test_fetch_club_links():
    # Mock the response from the requests.get call
    with patch("stadionowioprawcy_scrapper.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <body>
                <a href="/ekipy/arka-gdynia/">Arka Gdynia</a>
                <a href="/ekipy/lechia-gdansk/">Lechia Gdańsk</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        expected_clubs = ["arka-gdynia", "lechia-gdansk"]
        actual_clubs = fetch_club_links()
        assert actual_clubs == expected_clubs


def test_fetch_relations():
    # Mock the response for a specific club page
    with patch("stadionowioprawcy_scrapper.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <body>
                <h2>ZGODY</h2>
                <ul>
                    <li>Good Club 1</li>
                    <li>Good Club 2</li>
                </ul>
                <h2>KOSY</h2>
                <ul>
                    <li>Bad Club 1</li>
                </ul>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        # Create a temporary output file
        club_name = "test-club"
        fetch_relations(club_name)

        # Check if the CSV file was created and contains the expected data
        output_file = os.path.join("data", f"{club_name}.csv")
        assert os.path.exists(output_file)

        with open(output_file, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)
            assert header == ["Good Relations (ZGODY)", "Bad Relations (KOSY)"]
            rows = list(reader)
            assert rows == [["Good Club 1", "Bad Club 1"], ["Good Club 2", ""]]

        # Clean up the created file
        os.remove(output_file)


if __name__ == "__main__":
    pytest.main()
