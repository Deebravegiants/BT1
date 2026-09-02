### Title
Webhook shop and topic identity not covered by HMAC signature enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the `shop` and `topic` values used to route and scope the webhook are read from separate, unsigned HTTP headers. `Utils::HmacValidator.validate` only proves that the body was signed with the app secret; it proves nothing about which shop or topic that signed body is bound to. This is the exact bug class in the report: a field (`shop`, `topic`) that is acted upon by privileged logic but not covered by the same integrity check that gates that logic.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`shop` and `topic`, however, are pulled straight from the `X-Shopify-Shop-Domain` / `X-Shopify-Topic` headers, independently of the signed body: [2](#0-1) 

`Registry#process` validates only the body/HMAC pair, then dispatches the handler using the *unsigned* `shop` (and implicitly `topic`) values: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e., the body: [4](#0-3) 

The identity binding that should hold is:
`hmac_signed_bytes == bytes_that_determine(shop, topic)`

but the actual code enforces only:
`hmac_signed_bytes == raw_body`, while `shop` and `topic` are taken from headers outside that signed byte range.

Because a legitimate webhook delivery to *any* shop (including a shop an attacker fully controls, e.g. a free/dev store they install the app on) produces a genuine `(raw_body, hmac)` pair signed by Shopify with the app's real secret, an attacker who receives such a webhook can capture that valid `(body, hmac)` pair and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`) with a different shop's domain or a different topic. `HmacValidator.validate` still succeeds because it only checks the body bytes. `Registry#process` then invokes the app's handler with `WebhookMetadata` carrying the attacker-chosen `shop`/`topic`, even though the signature never certified that binding.

### Impact Explanation
This breaks tenant isolation for any app whose webhook handlers key persistence/business logic off `WebhookMetadata#shop` (the standard pattern documented for `Webhooks::Registry`/`WebhookHandler`). An attacker who owns one shop (freely obtainable, no privileged credential needed) can:
- Replay their own genuine, validly-signed webhook body but relabel it as coming from a victim shop, causing the app to write/update/act on data under the victim's tenant key using attacker-controlled body content.
- Relabel the topic of a validly-signed, benign payload as a sensitive topic (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`) to trigger privileged handler logic with a payload the attacker fully controls (since only the raw bytes are checked, not their semantic meaning tied to topic).

This qualifies as Critical (cross-tenant access) under the given impact categories, since the shop/tenant binding that the HMAC is supposed to certify is not actually enforced.

### Likelihood Explanation
Likelihood is high: no access token, no `client_secret`, and no privileged account are required — only the ability to install the app on any shop (including the attacker's own), capture one legitimate webhook delivery, and replay it with modified headers to the app's public webhook endpoint. This is fully exploitable by an unprivileged internet user interacting only with this gem's documented webhook-processing API (`Webhooks::Registry.process`).

### Recommendation
Include `shop` and `topic` (and any other header field the handler trusts) inside the HMAC-signed payload, or independently verify that the `shop`/`topic` headers match values cryptographically bound to the signed body (e.g., require Shopify's other anti-replay headers together with strict shop allowlisting per installation, and never trust `X-Shopify-Shop-Domain`/`X-Shopify-Topic` as authoritative unless they are provably part of what was signed). At minimum, document and enforce that consuming apps must independently verify `shop` against their known installed-shop list before trusting `WebhookMetadata#shop`, and treat topic/shop headers as adversarial input never covered by `HmacValidator.validate`.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`.
2. Trigger any webhook delivery (e.g. `orders/create`) — Shopify sends a POST with a genuine `raw_body`, `X-Shopify-Hmac-Sha256`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Capture `(raw_body, hmac)`.
4. Replay the same `raw_body`/`hmac` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally change `X-Shopify-Topic`).
5. `Webhooks::Registry#process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against `hmac`: [3](#0-2) 
6. The handler executes with `shop: "victim.myshopify.com"` and attacker-controlled body content, even though nothing Shopify-signed ever certified that this body belongs to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
