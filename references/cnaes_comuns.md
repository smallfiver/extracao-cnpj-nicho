# CNAEs de referencia por nicho

Tabela de partida para os nichos mais pedidos. O CNAE tem 7 digitos no
arquivo da Receita (sem pontuacao). Sempre confira 2-3 candidatos manualmente
(consulta publica de CNPJ) antes de rodar em escala -- CNAEs "genericos"
(ex: "Promocao de vendas") viram um balaio que contamina o nicho.

## Imobiliaria
| CNAE | Descricao |
|---|---|
| 6810201 | Compra e venda de imoveis proprios |
| 6810202 | Aluguel de imoveis proprios |
| 6821801 | Corretagem na compra e venda e avaliacao de imoveis |
| 6821802 | Corretagem no aluguel de imoveis |
| 6822600 | Gestao e administracao da propriedade imobiliaria |

## Construtora
| CNAE | Descricao |
|---|---|
| 4110700 | Incorporacao de empreendimentos imobiliarios |
| 4120400 | Construcao de edificios |
| 4211101 | Construcao de rodovias e ferrovias |
| 4213800 | Obras de urbanizacao |
| 4222701 | Construcao de redes de abastecimento de agua e esgoto |
| 4299599 | Outras obras de engenharia civil |

## Logistica / Transporte de carga
| CNAE | Descricao |
|---|---|
| 4930201 | Transporte rodoviario de carga municipal |
| 4930202 | Transporte rodoviario de carga intermunicipal/interestadual |
| 5211701 | Armazens gerais |
| 5211799 | Depositos de mercadorias |
| 5250803 | Agenciamento de carga |
| 5250805 | Operador de transporte multimodal - OTM |
| 5320202 | Servicos de entrega rapida |

## Marketing / Agencia
| CNAE | Descricao | Nota |
|---|---|---|
| 7311400 | Agencias de publicidade | melhor CNAE -- agencia de verdade |
| 7319004 | Consultoria em publicidade | bom, publicidade de verdade |
| 7319003 | Marketing direto | bom |
| 7320300 | Pesquisas de mercado e de opiniao publica | bom |
| 7319099 | Outras atividades de publicidade | bom |
| ~~7319002~~ | ~~Promocao de vendas~~ | **EVITAR**: balaio, atrai representante comercial, comercio e afins -- nao agencia |

## Academia / Fitness
| CNAE | Descricao | Nota |
|---|---|---|
| 9313100 | Atividades de condicionamento fisico | unico CNAE, mas agrupa musculacao, pilates, crossfit, personal -- filtre pelo NOME depois se precisar so um tipo |

## Como achar o CNAE de um nicho novo
1. Busque "CNAE [atividade]" no Google -- o portal da Receita e o CNAE.ibge
   tem os codigos completos.
2. Ou pesquise 2-3 empresas conhecidas do nicho na consulta publica de CNPJ
   (ex: minhareceita.org/{cnpj} ou casadosdados.com.br) e veja o campo
   `cnae_fiscal` delas.
3. Depois de escolher os codigos, rode uma extracao pequena (ex: 50
   candidatos) e cheque a distribuicao de CNAE antes de escalar -- se um
   CNAE dominar e trouxer lixo, tire ele da lista (foi o que aconteceu com
   "Promocao de vendas" acima).
