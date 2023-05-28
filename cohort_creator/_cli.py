"""Command line interface for cohort_creator."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from cohort_creator._parsers import global_parser
from cohort_creator._utils import check_participant_listing
from cohort_creator._utils import check_tsv_content
from cohort_creator._utils import validate_dataset_types
from cohort_creator.cohort_creator import construct_cohort
from cohort_creator.cohort_creator import get_data
from cohort_creator.cohort_creator import install_datasets
from cohort_creator.logger import cc_logger

cc_log = cc_logger()


def set_verbosity(verbosity: int | list[int]) -> None:
    if isinstance(verbosity, list):
        verbosity = verbosity[0]
    if verbosity == 0:
        cc_log.setLevel("ERROR")
    elif verbosity == 1:
        cc_log.setLevel("WARNING")
    elif verbosity == 2:
        cc_log.setLevel("INFO")
    elif verbosity == 3:
        cc_log.setLevel("DEBUG")


def cli(argv: Sequence[str] = sys.argv) -> None:
    """Entry point."""
    parser = global_parser()

    args, unknowns = parser.parse_known_args(argv[1:])

    datasets_listing = Path(args.datasets_listing[0]).resolve()
    participants_listing = Path(args.participants_listing[0]).resolve()
    output_dir = Path(args.output_dir[0]).resolve()

    dataset_types = args.dataset_types
    validate_dataset_types(dataset_types)

    verbosity = args.verbosity
    set_verbosity(verbosity)

    participants = check_tsv_content(participants_listing)
    check_participant_listing(participants)

    datasets = check_tsv_content(datasets_listing)  # not needed for now
    datasets_to_install = list(participants["DatasetName"].unique())

    sourcedata_dir = output_dir / "sourcedata"
    sourcedata_dir.mkdir(exist_ok=True, parents=True)

    if args.command == "install":
        install_datasets(
            datasets=datasets_to_install,
            sourcedata=sourcedata_dir,
            dataset_types=dataset_types,
        )
        return None

    datatypes = args.datatypes
    space = args.space

    if args.command == "get":
        jobs = args.jobs
        if isinstance(jobs, list):
            jobs = jobs[0]
        get_data(
            datasets=datasets,
            sourcedata=sourcedata_dir,
            participants=participants,
            dataset_types=dataset_types,
            datatypes=datatypes,
            space=space,
            jobs=jobs,
        )
        return None

    if args.command == "copy":
        construct_cohort(
            datasets=datasets,
            output_dir=output_dir,
            sourcedata_dir=sourcedata_dir,
            participants=participants,
            dataset_types=dataset_types,
            datatypes=datatypes,
            space=space,
        )
        return None