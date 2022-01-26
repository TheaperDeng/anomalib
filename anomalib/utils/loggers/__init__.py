"""Load PyTorch Lightning Loggers."""

# Copyright (C) 2020 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.


import os
from typing import Union

from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from pytorch_lightning.loggers.base import LightningLoggerBase

from .tensorboard import AnomalibTensorBoardLogger
from .wandb_logger import AnomalibWandbLogger

__all__ = ["AnomalibTensorBoardLogger", "get_logger", "AnomalibWandbLogger"]
AVAILABLE_LOGGERS = ["tensorboard", "wandb"]


class UnknownLogger(Exception):
    """This is raised when the logger option in `config.yaml` file is set incorrectly."""


def get_logger(config: Union[DictConfig, ListConfig]) -> Union[LightningLoggerBase, bool]:
    """Return a logger based on the choice of logger in the config file.

    Args:
        config (DictConfig): config.yaml file for the corresponding anomalib model.

    Raises:
        ValueError: for any logger types apart from false and tensorboard

    Returns:
        Union[LightningLoggerBase, Iterable[LightningLoggerBase], bool]: Logger
    """
    logger: Union[LightningLoggerBase, bool]

    if config.project.logger in [None, False]:
        logger = False

    elif config.project.logger == "tensorboard":
        logger = AnomalibTensorBoardLogger(
            name="Tensorboard Logs",
            save_dir=os.path.join(config.project.path, "logs"),
        )

    elif config.project.logger == "wandb":
        wandb_logdir = os.path.join(config.project.path, "logs")
        os.makedirs(wandb_logdir, exist_ok=True)
        logger = AnomalibWandbLogger(
            project=config.dataset.name,
            name=f"{config.dataset.category} {config.model.name}",
            save_dir=wandb_logdir,
        )

    else:
        raise UnknownLogger(
            f"Unknown logger type: {config.project.logger}. "
            f"Available loggers are: {AVAILABLE_LOGGERS}.\n"
            f"To enable the logger, set `project.logger` to `true` or use one of available loggers in config.yaml\n"
            f"To disable the logger, set `project.logger` to `false`."
        )

    return logger
