Projeto de conclusão de curso desenvolvido por Luiza Queiroz e Allysson Rodrigues, com orientação de Rodolfo Viana (github.com/rodolfo-viana).

O objetivo deste projeto é automatizar o fluxo de novos pedidos de associações jornalísticas feitos à Ajor (Associação de Jornalismo Digital).

O processo, antes feito manualmente, consiste em checar se a associação em questão possui um CNPJ ativo há mais de um ano
e se disponibiliza uma forma válida de contato com a redação em seu site.

O código visa realizar essa análise de forma automática, a partir de uma consulta via API a uma base de dados de CNPJs cadastrados na Receita Federal
e por meio de uma busca de palavras-chaves no site da associação.

Feita essa análise, o código envia um email de forma automática para a associação postulante informando os próximos passos a serem tomados.
