### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read from unauthenticated HTTP headers. Because a single app-wide `api_secret_key` is used to validate every installation's webhooks, any party who can obtain one genuine (body, HMAC) pair signed by that shared secret can replay it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header, and `HmacValidator.validate` will still accept it — the handler then runs as if the event came from a different shop.

### Finding Description
`Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are pulled straight from headers, none of which are mixed into the signable string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, and once that passes, forwards `request.shop`, `request.topic`, and `request.webhook_id` straight to the handler with no further binding check: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` header — since `to_signable_string` is body-only, the HMAC proves nothing about which shop, topic, or webhook the payload is associated with: [4](#0-3) 

The identity binding that should hold is:
`shop asserted to handler (request.shop, read from header)` == `shop the HMAC-signed bytes were actually generated for`

This binding is not enforced anywhere in the library — the HMAC only certifies "these body bytes were produced by someone holding `api_secret_key`," not "for this shop domain."

Because Shopify apps use one `client_secret`/`api_secret_key` per app across *all* installing shops (this mirrors the Notional report's theme: a value trusted for the wrong scope — there, `maxRedeem()` return value was blindly trusted as the settleable balance; here, the body-only HMAC is blindly trusted as proof of shop identity), a person who legitimately installs the app on their own store (no privileged access required) receives genuine webhooks with valid HMACs computed with the shared secret. They can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) for a victim shop. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` dispatches the handler with the attacker-controlled `shop` value now treated as authoritative merchant identity — a cross-tenant identity-binding break implemented entirely inside this gem's own `Webhooks::Request`/`Registry` code, not merely a case of the host app misusing the API.

### Impact Explanation
This crosses the "cross-tenant access" bar: a handler that persists or acts on webhook data keyed by `data.shop` (as the gem's own `WebhookMetadata` construction demonstrates) will attribute attacker-controlled body content to a victim shop identifier, without requiring the attacker to hold that victim's credentials, access token, or `api_secret_key`. It satisfies the required binding-break pattern: "a field acted on but not covered by the HMAC."

### Likelihood Explanation
Requires only: (1) ability to install/create a shop on the target app to legitimately receive at least one signed webhook (freely obtainable, unprivileged), and (2) ability to POST arbitrary headers/body to the app's public webhook receiver endpoint (standard for any internet-reachable HTTP endpoint). No secrets, tokens, or social engineering needed.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable content, or otherwise cryptographically or out-of-band bind the asserted `shop` header to the specific installation before dispatching to handlers (e.g., validate against the shop's own per-installation secret/session rather than a single app-wide secret, or require the consuming application to cross-check the shop against its own webhook subscription record for that `webhook_id`/`topic` pair before trusting `request.shop`).

### Proof of Concept
1. Attacker creates a free/dev shop `attacker.myshopify.com` and installs the target app, receiving legitimate webhooks signed with the app's shared `api_secret_key`.
2. Attacker captures one webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker POSTs to the app's public webhook endpoint with the same body `B` and HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` (via `Request#to_signable_string` returning only `B`) succeeds, since the header change doesn't affect the signed bytes: [1](#0-0) 
5. `Registry.process` dispatches the handler with `shop: "victim.myshopify.com"`, `body: parsed_body(B)`, causing the app to process attacker-chosen content under the victim's tenant identity: [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
