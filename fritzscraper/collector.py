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
        rx, tx = self._session.docsis_info()

        for rx_channel_idx, rx_channel in rx.iterrows():
            rx_channel_id = rx_channel[0]
            rx_channel_carrier = rx_channel[1]  # MHz
            # rx_channel_modulation = rx_channel[2]
            rx_channel_power_level = rx_channel[3]  # dBmV
            rx_channel_mse = rx_channel[4]  # dB
            rx_channel_latency = rx_channel[5]  # ms
            rx_channel_correctable_errors = rx_channel[6]
            rx_channel_uncorrectable_errors = rx_channel[7]

            channel_id.add_metric(['rx', rx_channel_idx], int(rx_channel_id))
            channel_carrier.add_metric(['rx', rx_channel_idx], float(rx_channel_carrier))
            channel_power_level.add_metric(['rx', rx_channel_idx], float(rx_channel_power_level))
            channel_mse.add_metric(['rx', rx_channel_idx], float(rx_channel_mse))
            channel_latency.add_metric(['rx', rx_channel_idx], float(rx_channel_latency))
            channel_correctable_errors.add_metric(['rx', rx_channel_idx], int(rx_channel_correctable_errors))
            channel_uncorrectable_errors.add_metric(['rx', rx_channel_idx], int(rx_channel_uncorrectable_errors))

        for tx_channel_idx, tx_channel in tx.iterrows():
            tx_channel_id = tx_channel[0]
            tx_channel_carrier = tx_channel[1]  # MHz
            # tx_channel_modulation = tx_channel[2]
            # tx_channel_multiplexing_scheme = tx_channel[3]
            tx_channel_power_level = tx_channel[4]  # dBmV

            channel_id.add_metric(['tx', tx_channel_idx], int(tx_channel_id))
            channel_carrier.add_metric(['tx', tx_channel_idx], float(tx_channel_carrier))
            channel_power_level.add_metric(['tx', tx_channel_idx], float(tx_channel_power_level))

        yield channel_id
        yield channel_carrier
        yield channel_power_level
        yield channel_mse
        yield channel_latency
        yield channel_correctable_errors
        yield channel_uncorrectable_errors
