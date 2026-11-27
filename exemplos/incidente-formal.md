# INC-2026-0147 — Degradação do backup noturno

**Documento:** INC-2026-0147
**Data desta versão:** 2026-11-20
**Versão:** 1.0
**Status:** Em acompanhamento
**Classificação:** Interno

# OBJETIVO DO DOCUMENTO

Registrar a degradação do backup noturno do servidor de arquivos, as causas
identificadas e as ações de contenção — exemplo fictício para demonstrar o
template formal.

# Resumo executivo

Na madrugada de 2026-11-19 o backup completo do servidor de arquivos excedeu
a janela de 6 horas e terminou com erro de espaço no destino. Nenhum dado de
produção foi perdido; o último backup íntegro é de 2026-11-18. A causa raiz
foi o crescimento do volume de mídia (+38% em 30 dias) sem ajuste da cota do
destino.

# 1. Linha do tempo

1. 02:00 — início do backup completo (agendado).
2. 07:42 — job aborta com erro de espaço no destino.
3. 08:15 — equipe acionada; snapshot manual executado com sucesso.
4. 09:30 — cota do destino ampliada em caráter emergencial.

| CAMPO | AVALIAÇÃO |
| --- | --- |
| Fato | Backup de 2026-11-19 falhou por falta de espaço |
| Fato | Último backup íntegro: 2026-11-18 |
| Hipótese | Crescimento de mídia seguirá pressionando a cota |

# Responsáveis e validação

| NOME | FUNÇÃO | PARTICIPAÇÃO |
| --- | --- | --- |
| Maria Silva | Infraestrutura | Diagnóstico e contenção |
| João Souza | Segurança | Revisão do relatório |

# Aprovação

| VALIDAÇÃO | RESPONSÁVEL | DATA |
| --- | --- | --- |
| Conteúdo técnico | Maria Silva | 2026-11-20 |
| Publicação | João Souza | 2026-11-20 |
