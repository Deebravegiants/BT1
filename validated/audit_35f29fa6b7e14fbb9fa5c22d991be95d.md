[1](#0-0)  confirms the vulnerability: the webhook `hmac` is computed only from `@raw_body`, while `shop`, `topic`, and `webhook_id` are read directly from client-supplied HTTP headers that are never included in the signed payload.

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while the HMAC binds only the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is later handed to application webhook handlers from the `x-shopify-shop-domain`/`shopify-shop-domain` header, but the HMAC signature verified by `Registry.process` only covers the raw request body. This breaks the identity binding `shop_header == shop_bound_by_hmac`, which should hold but does not.

### Finding Description
`Utils::HmacValidator.validate` computes the expected HMAC purely from `verifiable_query.to_signable_string`, and for webhook requests that method returns only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body authenticity) before dispatching to the registered handler with `request.shop`, `request.topic`, and `request.webhook_id` taken at face value: [4](#0-3) 

Because the signature never covers the headers, any request that carries a previously-observed valid `(raw_body, hmac)` pair (for example, a webhook the attacker legitimately received for their own shop after installing the target app once) remains HMAC-valid no matter what `shop-domain`, `topic`, or `webhook-id` headers are attached to it. An attacker fully controls those header values while keeping the HMAC check passing, so they can present a foreign/victim shop's identity, or a different topic, to the handler while replaying a body they legitimately obtained for their own tenant.

### Impact Explanation
Any application handler that trusts `WebhookMetadata#shop` (or `#topic`) as an authenticated tenant identifier — e.g., to look up/act on a specific merchant's session, mark a shop as uninstalled, or route to shop-specific compliance/GDPR data-erasure handlers — can be made to act on the wrong tenant's data or trigger topic-specific logic under an attacker-chosen shop identity, i.e. cross-tenant access, using only a single legitimately-received webhook body/HMAC pair from the attacker's own store.

### Likelihood Explanation
The attacker doesn't need `api_secret_key`, an access token, or any privileged account beyond installing the target app on a shop they control (which any unprivileged internet user with a free Shopify dev store can do) to obtain one valid `(raw_body, hmac)` pair, then replay it to the app's public webhook endpoint with attacker-chosen `shop-domain`/`topic`/`webhook-id` headers.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed payload used for HMAC verification (or otherwise cryptographically bind them to the body), and document clearly that these headers must not be treated as authenticated unless independently verified against the request body/signature.

### Proof of Concept
1. Install the target Shopify app on an attacker-owned development store (`attacker-shop.myshopify.com`) and register a webhook subscription for a topic the app handles specially (e.g., `app/uninstalled` or a GDPR data-request topic).
2. Capture the resulting webhook HTTP POST that Shopify sends: raw body `B`, and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`).
3. Replay a new POST to the same public webhook endpoint using the identical body `B` and header `x-shopify-hmac-sha256: H`, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only re-computes the HMAC over `B`, which is unchanged; `Registry.process` in `lib/shopify_api/webhooks/registry.rb` then dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)` to the app's handler as if it were an authentic event for `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
