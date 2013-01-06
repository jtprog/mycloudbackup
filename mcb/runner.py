import logging
from mcb.outputs import OutputPipe

class Runner(object):

  def __init__(self, config=None):
    self.services = []
    self.outputs = []

    logging.basicConfig(level=logging.DEBUG)
    self.logger = logging.getLogger('mcb')

    if config:
      self.loadConfig(config)

  def loadConfig(self, config):
    self.config = config

    self.services = config.getServices()
    self.outputs = config.getOutputs()

  def saveConfig(self):
    self.config.importServices(self.services)
    self.config.importOutputs(self.outputs)

    self.config.save()

  def run(self):
    pipe = OutputPipe(self.outputs)
    pipe.prepare()
    pipe.setLogger(self.logger)

    self.logger.info('Backing up {count} services'.format(
      count=len(self.services)
    ))
    for service in self.services:
      self.logger.info('Backing up ' + service.__class__.__name__)

      service.validate()

      pipe.setPrefix(service.getOutputPrefix())
      service.setLogger(self.logger)
      service.setOutput(pipe)
      service.runBackup()

    self.logger.info('All done')

    self.logger.info('Saving data...')
    self.saveConfig()

