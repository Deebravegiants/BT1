### Title
Webhook shop-domain (tenant) identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The gem validates the HMAC of an incoming webhook against only the raw request body, while the `shop-domain` and `topic` headers used to attribute the webhook to a specific merchant/tenant are read directly from unauthenticated HTTP headers and never included in the signed payload. This mirrors the "field acted on but not covered by the HMAC" bug class in the report: `assetToken`/`underlyingToken` were acted upon without being covered by validation checks that applied elsewhere.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only the body-derived HMAC, then immediately trusts `request.shop` and `request.topic` (both unauthenticated headers) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop attributed to webhook == shop that actually generated the signed body`. Because the HMAC only signs the body, this binding is never enforced — `hmac_valid(body) == true` says nothing about which shop the `shop-domain` header claims. An unprivileged internet user who can obtain any one valid `(body, hmac)` pair signed with the app's secret (e.g., by installing the app on their own free/dev store and receiving a legitimate webhook for an event they trigger) can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `Utils::HmacValidator.validate` will still return `true` because it only recomputes the signature over `@raw_body`: [4](#0-3) 

The forged request then flows to the host app's handler tagged with an attacker-chosen `shop`, letting the attacker inject data attributed to another merchant's tenant.

### Impact Explanation
This breaks the tenant/shop identity binding that host applications rely on to route and store webhook data per-merchant, enabling cross-tenant data injection/confusion — data that legitimately originated from the attacker's own store can be made to appear as originating from a victim shop. This matches the Critical/High "cross-tenant access" impact category, since it lets one tenant's actions be misattributed to and processed under another tenant's identity.

### Likelihood Explanation
Requires only the ability to install the app on any Shopify store (including a free development store) to legitimately harvest a valid `(body, hmac)` pair for a chosen topic, plus knowledge of a victim's `myshopify.com` domain (public information) — no privileged credentials, secrets, or access tokens are needed. The webhook endpoint is by design internet-reachable and unauthenticated aside from the HMAC.

### Recommendation
Include the `shop-domain` (and ideally `topic`) header values in the HMAC signable string, or otherwise cryptographically bind the claimed shop to the signed payload, so that `Utils::HmacValidator.validate` fails if the shop attribution has been tampered with. At minimum, document that consuming applications must cross-check `request.shop` against a shop they already have an active, previously-verified session/installation for before trusting webhook data.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger an event so Shopify sends a legitimately signed webhook `(raw_body, hmac)` to the app's webhook endpoint.
2. Capture that `(raw_body, hmac)` pair.
3. Replay an HTTP POST to the same webhook endpoint with the identical `raw_body` and `shopify-hmac-sha256` header, but set `shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the signature only from `raw_body` (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`) and succeeds.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata` carrying the spoofed `shop: "victim-shop.myshopify.com"`, causing the host application to process attacker-supplied data as if it belonged to the victim tenant.

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
