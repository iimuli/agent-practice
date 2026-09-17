

class DosingError(Exception):
    """Kantaluokka kaikille annostelun virheille."""
    pass

class MissingPatientDataError(DosingError):
    """Heitetään kun pakollinen tieto (esim. lapsen paino) puuttuu."""
    pass

class NoMatchingRuleError(DosingError):
    """Heitetään kun syötetyillä parametreilla ei löydy lääke- tai hoito-ohjetta."""
    pass

class NoMatchingSymptomsError(Exception):
    """Heitetään kun oire kuvaa ei löydy tietokannasta."""
    pass