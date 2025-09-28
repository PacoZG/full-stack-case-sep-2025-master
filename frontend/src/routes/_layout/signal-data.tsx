import { createFileRoute } from '@tanstack/react-router';
import SignalData from '../signal-data';

export const Route = createFileRoute('/_layout/signal-data')({
  component: SignalData,
});

