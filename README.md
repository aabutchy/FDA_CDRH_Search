# The FDA CDRH Search Repo:

## _For finding, scraping, and manipulating FDA cleared devices via device submission numbers._

This repository is a broad programmatic manner to automatically pull FDA 510(k) and De Novo summaries from the FDA's database for easily parsing/manipulating the data therein.

In this repository, there are classes for easy scraping FDA 510ks and De Novo devices based only on a Submission Number (eg "K000000" or "DEN000000"). In addition, there are helful functions for downloading the full list of FDA 510(k) devices as databased by the FDA and updated on a monthly basis. Combined, these two options allow a user to conduct rudimentary FDA predicate device searches in a near-automatic fashion. Below, I walk through a small tutorial on how to employ this repo to conduct pointed predicate-device searches.

## FDA Database Resources

In writing this repository, it is apparent that one could use this code to querey the FDA database to identify all 510(k)'s and De Novo's and build a large database of all ~100,000 cleared and granted devices. While this was not the intent of the code, it would be irresponsible if I did not acknowledge this possibility and council against it. The FDA CDRH provides this information at no cost, and it is a useful tool for medical device developers and companies. It would be a loss for the greater community if such information was put behind a firewall, paywall, or other rate-limiting measure. If you are interested in routinely and aggressively querying the FDA's servers, please be mindful to not overly burden the FDA's resources and website.

## Inspiration and References

- [tbiscof's Github "FDA" repository](https://github.com/tsbischof/fda/tree/master) - Really cool predicate tracing methodology.
- [McClain98's Github "FDAexplorer" repository ](https://github.com/McClain98/FDAexplorer/tree/main) - FDA database download and manipulation.
- [JustIceQAQ's Github "Downloads_510K_Data" repository](https://github.com/JustIceQAQ/Downloads_510K_Data) - FDA database parsing.

## Useful FDA Resources

- [List of FDA Databases](https://www.fda.gov/medical-devices/products-and-medical-procedures/device-approvals-denials-and-clearances)
- [FDA Searchable 510k Database](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm)
- [FDA Searchable De Novo Database](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/denovo.cfm)
- [FDA Searchable PMA Database](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMA/pma.cfm)
- [FDA Downloadable 510k Database (updated monthly)](https://www.fda.gov/medical-devices/510k-clearances/downloadable-510k-files)
- [FDA Database of FDA Databases](https://www.fda.gov/medical-devices/device-advice-comprehensive-regulatory-assistance/medical-device-databases)
- [FDA Recently Approved Devices and Database](https://www.fda.gov/medical-devices/device-approvals-denials-and-clearances/recently-approved-devices)
