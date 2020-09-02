import logging

from prometheus_client.metrics_core import CounterMetricFamily, GaugeMetricFamily

from fritzscraper.session import FritzSession

logger = logging.getLogger(__name__)


class FRITZBoxCollector:
    def __init__(self, host: str, user: str, password: str):

        self._session = FritzSession(host, user, password)

    def collect(self):
        logger.info('Collecting data')

        channel_id = GaugeMetricFamily('docsis_channel_id', 'Channel ID', labels=['direction', 'index'])
        channel_carrier = GaugeMetricFamily('docsis_channel_carrier_mhz', 'Channel carrier frequency',
                                            labels=['direction', 'index'])
        channel_power_level = GaugeMetricFamily('docsis_channel_power_level_dbmv', 'Channel power level',
                                                labels=['direction', 'index'])
        channel_mse = GaugeMetricFamily('docsis_channel_mse_db', 'Channel mean squared error (MSE)',
                                        labels=['direction', 'index'])
        channel_latency = GaugeMetricFamily('docsis_channel_latency_ms', 'Channel latency',
                                            labels=['direction', 'index'])
        channel_correctable_errors = CounterMetricFamily('docsis_channel_correctable_errors',
                                                         'Number of correctable errors', labels=['direction', 'index'])
        channel_uncorrectable_errors = CounterMetricFamily('docsis_channel_uncorrectable_errors',
                                                           'Number of uncorrectable errors',
                                                           labels=['direction', 'index'])

        # Handle 403 here
        rx, tx = self._session.docsis_info_new()

        for rx_channel in rx:
            rx_channel_idx = rx_channel['channel']
            rx_channel_id = rx_channel['channelID']
            rx_channel_carrier = rx_channel['frequency']  # MHz
            # rx_channel_modulation = rx_channel[2]
            rx_channel_power_level = rx_channel['powerLevel']  # dBmV
            rx_channel_mse = rx_channel['mse']  # dB
            rx_channel_latency = rx_channel['latency']  # ms
            rx_channel_correctable_errors = rx_channel['corrErrors']
            rx_channel_uncorrectable_errors = rx_channel['nonCorrErrors']

            labels = ['rx', str(rx_channel_idx)]
            channel_id.add_metric(labels, int(rx_channel_id))
            channel_carrier.add_metric(labels, float(rx_channel_carrier))
            channel_power_level.add_metric(labels, float(rx_channel_power_level))
            channel_mse.add_metric(labels, float(rx_channel_mse))
            channel_latency.add_metric(labels, float(rx_channel_latency))
            channel_correctable_errors.add_metric(labels, int(rx_channel_correctable_errors))
            channel_uncorrectable_errors.add_metric(labels, int(rx_channel_uncorrectable_errors))

        for tx_channel in tx:
            tx_channel_idx = tx_channel['channel']
            tx_channel_id = tx_channel['channelID']
            tx_channel_carrier = tx_channel['frequency']  # MHz
            # tx_channel_modulation = tx_channel[2]
            # tx_channel_multiplexing_scheme = tx_channel[3]
            tx_channel_power_level = tx_channel['powerLevel']  # dBmV

            labels = ['tx', str(tx_channel_idx)]
            channel_id.add_metric(labels, int(tx_channel_id))
            channel_carrier.add_metric(labels, float(tx_channel_carrier))
            channel_power_level.add_metric(labels, float(tx_channel_power_level))

        yield channel_id
        yield channel_carrier
        yield channel_power_level
        yield channel_mse
        yield channel_latency
        yield channel_correctable_errors
        yield channel_uncorrectable_errors
