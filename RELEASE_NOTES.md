### Version 1.3.1
__Changes__
- make sure subsample fastq has fixed IDs for HISEQ edge case

### Version 1.3.0
__Changes__
- updated Kaiju program to v1.9.0 (released 2022-05-12)
1;95;0c- didn't update progenomes (ver is 2021-03-02)
- updated nr_euk refdata to 2022-03-10
- updated nr refdata to 2022-03-10
- updated refseq to 2022-03-23
- updated fungi to 2022-03-29
- updated viruses to 2022-03-29
- updated plasmids to 2022-04-10
- updated rvdb to 2022-04-07
- more careful handling of exceptional Read IDs in _random_subsample_reads()
- set to current default of -e max_mismatches=3
- set to current default of -s min_match_score=65
- set to current default of -E max_e-value=0.01

### Version 1.2.0
__Changes__
- updated to early 2021 database releases (range of dates)
- added new databases as selectable options: viruses, plasmids, rvdb, fungi
- updated to Kaiju version 1.7.4

### Version 1.1.6
__Changes__
- prepped version numbers for release
- improved error handling message : Updating the message a user receives when their parameters are too strict and no output is produced.

### Version 1.1.5
__Changes__
- updated documentation to reflect 2020-05-25 releases

### Version 1.1.4
__Changes__
- updated Kaiju to version 1.7.3
- updated Kaiju databases to the 2020-05-25 releases

### Version 1.1.3
__Changes__
- fixed a read_id edge case

### Version 1.1.2
__Changes__
- fixed default database value

### Version 1.1.1
__Changes__
- fixed error due to unpaired rev reads

### Version 1.1.0
__Changes__
- updated kaiju to v1.7.2 (released 2019-07-12)
- updated Kaiju reference databases; now using 2019-06-25 versions
- added new required flags -i and -j to kaiju binary
- renamed kaijuReport binary to kaiju2table
- removed discontinued flag -i from kaiju2table
- addressed new kaiju database directory structure
- added new logic to address five-column kaiju report output

### Version 1.0.6
__Changes__
- update docs

### Version 1.0.5
__Changes__
- fixed biom param check in code

### Version 1.0.4
__Changes__
- removed deprecated BIOM output object

### Version 1.0.3
__Changes__
- updated base image to sdkbase2

### Version 1.0.2
__Changes__
- changed citation to PLOS format

### Version 1.0.1
__Changes__
- Fixed random subsample of Single End Libraries

### Version 1.0.0
- Initial release version

### Version 0.0.1
- Initial dev version
