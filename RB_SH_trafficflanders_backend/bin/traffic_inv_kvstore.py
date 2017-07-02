# $Id: traffic_inv_kvstore.py 2016-07-02 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert

###############################
####### Logger functions ######
###############################

# logging setup subroutine
def setup_logging():
	"""
	Setup logging
	Log is written to /opt/splunk/var/log/splunk/traffic_inv_kvstore.log
	"""
	FILENAME = os.path.splitext(os.path.basename(__file__))[0]
	logger = logging.getLogger('splunk.' + FILENAME)
	logger.setLevel(logging.INFO)
	SPLUNK_HOME = os.environ['SPLUNK_HOME']
	
	LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
	LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
	LOGGING_STANZA_NAME = 'python'
	LOGGING_FILE_NAME = FILENAME + ".log"
	BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
	LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
	
	splunk_log_handler = logging.handlers.RotatingFileHandler(
		os.path.join(_SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
	splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
	logger.addHandler(splunk_log_handler)
	splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE,
						LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
	
	return logger

class TrafficInvToKVStore(Script):
	"""
	Main class for the modular input inheriting from the Script class.
	The Script class is an abstract class shipped with the Splun SDK and used for modular inputs specifically.
	"""
	
	# subroutine to get the scheme from the modular input
	def get_scheme(self):
		# Returns scheme.
		scheme = Scheme("Flanders Traffic inventory to KV store modular input")
		scheme.description = "Captures inventory information from the traffic related sensors in Flanders via its open data platform and pushes this to the KV store."
   
# main entry point of the modular input
if __name__ == "__main__":
    sys.exit(TrafficInvToKVStore().run(sys.argv))