# Job Count

`job-count` is a python CLI tool for counting the number of job postings on LinkedIn.

Perfect for those of us that are curious (anxious) about the trajectory of a particular industry (software engineering) in the wake of change (the AI apocalypse).

`job-count` is designed to be run as a cronjob to collect data over a period of time.

## Requirements

- **LinkedIn account** - preferably not the one you actually use, in case it gets banned.
- [**uv**](https://github.com/astral-sh/uv) - `0.4.30+`, for installation.

- **Chrome** or **Firefox** - this is a scraping tool!

## Installation

1. Create a venv with the correct python version:

```bash
uv venv -p 3.13.0
```

2. Install as a package:

```bash
uv pip install git+https://github.com/archie-judd/job-count.git
```

3. Activate your venv

```bash
source .venv/bin/activate
```

4. Check installation worked:

```bash
job-count --version
```

## Login to LinkedIn

To check for LinkedIn jobs, you must provide login credentials to the CLI.

Run the following command, which will open a browser (Chrome by default, but Firefox is available too), and take you to the LinkedIn login page.

```bash
job-count login
```

Enter your details, and login, completing any Captcha questions. Upon login, the cookies will be saved (at `~/.local/share/job-count`, unless another location is specified) and the browser window will close.

Run `job-count login -h` to see the options available for this command.

## Query

Having logged in, you can count the number of postings for various jobs with the `query` command. The query command accepts either list of terms, or an input file.

To query with terms:

```bash
job-count query --terms "Ice Sculptor,Honolulu" "Panda Fluffer,Greater Tokyo"
```

Or with an input file:

```bash
job-count query --input-file <path/to/input/file.csv>
```

The command takes an input `.csv` file of format:

| job_title     | location      |
| ------------- | ------------- |
| Ice Sculptor  | Honlulu       |
| Panda Fluffer | Greater Tokyo |
| ...           | ...           |

You can see an example at `sample_data/input.csv`.

You can optionally write the results of the query to an output file as follows:

```bash
job-count query --terms "Ice Sculptor,Honolulu" "Panda Fluffer,Greater Tokyo" --output-file <path/to/output.csv>
```

The results will be written in the format:

| job_title     | location      | ts                       | count |
| ------------- | ------------- | ------------------------ | ----- |
| Ice Sculptor  | Honlulu       | 2024-01-25T18:07:31.180Z | 19    |
| Panda Fluffer | Greater Tokyo | 2024-01-25T18:07:32.010Z | 203   |
| ...           | ...           | ...                      | ...   |

You can see an example at `sample_data/output.csv`.

If your output file doesn't exist, it will be created, if there is already data in your output file, it will be appended to.

Run `job-count count-jobs -h` for more options.

## Clear cookies

Run `job-count clear-cookies` to clear your cookies. You will need to run `job-count login` again.

## FAQ:

1. Does `job-count` do anything nefarious with my credentials?

No, you read the code to be sure.

2. How can I run `job-count` as a cron job?

The easiest way is probably via [crontab](https://man7.org/linux/man-pages/man5/crontab.5.html). Here is an example that runs at 9pm each day:

```bash
0 21 * * * <path/to/job-count> query --input-file <path/to/input.csv> --output-file <path/to/output.csv> --log-file <path/to/log-file.log> --verbose

```

Run `which job-count` from your activated venv to get the path.

## TODO:

- `job-count plot` command, to plot results.
- Support other job hunting websites - Indeed, Reed, Monster etc.
