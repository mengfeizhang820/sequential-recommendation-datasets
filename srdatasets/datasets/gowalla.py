import glob
import gzip
import logging
import os
import shutil
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
import wget
from pandas import DataFrame

from srdatasets.datasets.dataset import Dataset

logger = logging.getLogger(__name__)


class Gowalla(Dataset):

    __download_url__ = "https://snap.stanford.edu/data/loc-gowalla_totalCheckins.txt.gz"
    __corefile__ = "loc-gowalla_totalCheckins.txt"

    def download(self) -> None:
        try:
            wget.download(self.__download_url__, out=self.home)
            logger.info("Download successful, unzipping...")
        except:
            logger.exception("Download failed, please retry")
            for f in glob.glob(self.home.joinpath("*.tmp")):
                os.remove(f)
            return

        zipfile_name = os.path.basename(urlparse(self.__download_url__).path)
        zipfile_path = self.home.joinpath(zipfile_name)
        unzipfile_path = self.home.joinpath(self.__corefile__)

        with gzip.open(zipfile_path, "rb") as f_in:
            with open(unzipfile_path, "w") as f_out:
                shutil.copyfileobj(f_in, f_out)
        logger.info("Finished, dataset location: %s", self.home)

    def transform(self) -> DataFrame:
        """ Time: yyyy-mm-ddThh:mm:ssZ -> timestamp """
        df = pd.read_csv(
            self.home.joinpath(self.__corefile__),
            sep="\t",
            names=["user_id", "timestamp", "latitude", "longtitude", "item_id"],
            index_col=False,
            usecols=[0, 1, 4],
            converters={
                "timestamp": lambda x: int(
                    datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ").timestamp()
                )
            },
        )
        return df
