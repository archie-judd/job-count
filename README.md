# Job Count - Count LinkedIn Job Postings

`job-count` is a python CLI tool for counting the number of job postings on LinkedIn.

Perfect for those of us that are curious (anxious) about the trajectory of a particular industry (software engineering) in the wake of change (the AI apocalypse).

`job-count` is designed to be run as a cronjob to collect data over a period of time.

## Requirements

- **LinkedIn account** - preferably not the one you actually use, in case it gets banned.
- **uv** - 0.4.30+, for installation.

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

3. Check installation worked:

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

## Count jobs

Having logged in, you can count the number of postings for various jobs with the following command:

```bash
job-count count-jobs </path/to/input/file.csv> </path/to/output/file.csv>
```

Run `job-count count-jobs -h` for more options.

The command takes an input `.csv` file of format (you can see an example at `sample_data/input.csv`):

| job_title     | location      |
| ------------- | ------------- |
| Ice Sculptor  | Honlulu       |
| Panda Fluffer | Greater Tokyo |
| ...           | ...           |

It will write the output which will look like (you can see an example at `sample_data/output.csv`):

| job_title     | location      | ts                       | count |
| ------------- | ------------- | ------------------------ | ----- |
| Ice Sculptor  | Honlulu       | 2024-01-25T18:07:31.180Z | 19    |
| Panda Fluffer | Greater Tokyo | 2024-01-25T18:07:32.010Z | 203   |
| ...           | ...           | ...                      | ...   |

If your output file doesn't exist, it will be created, if there is already data in your output file, it will be amended to.

## Clear cookies

Run `job-count clear-cookies`

To clear your cookies.

## TODO:

- `job-count plot` command, to plot results.

## FAQ:

1. Does `job-count` do anything nefarious with my credentials?

No, but read code to be sure.
