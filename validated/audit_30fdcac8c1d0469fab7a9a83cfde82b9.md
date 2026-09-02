### Title
Webhook `shop-domain` header is trusted for tenant identity but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that gets passed to app handler code from an unauthenticated header, while the HMAC signature that `Utils::HmacValidator` checks only covers the raw request body. This breaks the binding "bytes verified == bytes/fields the app acts on," letting a replayed, HMAC-valid webhook be relabeled to a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from HTTP headers, which are never part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` computes/verifies the HMAC only against `to_signable_string` (the body): [3](#0-2) 

`Webhooks::Registry.process` validates that HMAC and then immediately trusts `request.shop` as the tenant identity handed to the app's handler: [4](#0-3) 

That value flows into `WebhookMetadata#shop`, a plain `String` field with no further verification: [5](#0-4) 

Equality that should hold: `hmac_signed_bytes == bytes_the_app_acts_on_for_tenant_identity`. Here `hmac_signed_bytes = raw_body` while `bytes_the_app_acts_on_for_tenant_identity = shop-domain header`, which are disjoint. Because the app's `client_secret`/`api_secret_key` used for webhook verification is shared across every shop/store that has the app installed (it is not per-shop), any party that legitimately receives one valid `(body, hmac)` pair for their own store (e.g., by installing the app on a store they control, or capturing/replaying a delivery) can resend that exact `(body, hmac)` pair while substituting a different value in `X-Shopify-Shop-Domain`/`shopify-shop-domain`. `HmacValidator.validate` will still return `true` because it never inspects the shop header, and `Registry.process` will dispatch to the app's handler with `WebhookMetadata#shop` set to the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity spoof at the trust boundary the gem is responsible for: the gem's whole purpose in `Registry.process` is to authenticate an inbound webhook and hand the app a `WebhookMetadata` it can trust to belong to the named shop. Since `shop` is unauthenticated, a host app that (reasonably, per this gem's documented contract) uses `data.shop` from a validated webhook to route/attribute data will have another tenant's records overwritten, deleted, or otherwise processed under the wrong shop -- a cross-tenant access issue with no additional privilege required beyond running an app that has ever received one legitimate webhook.

### Likelihood Explanation
Any merchant that installs the app on their own store receives real webhooks (valid body+HMAC) for it, giving them freely-obtainable attacker material. Replaying it with a different `shop-domain` header value is a trivial HTTP-header edit; it does not require the `client_secret`, an access token, or any credential beyond normal app usage. This is a low-effort, unprivileged-internet-user-reachable path.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) claim to the signature: either include the shop domain in the signable string used for HMAC verification, or require the caller to independently confirm `request.shop` corresponds to a shop with an active session/installation for this app before trusting it in `WebhookMetadata`. At minimum, document/enforce that `Registry.process` callers must cross-check `request.shop` against their own known-installed-shop list rather than treating it as authenticated solely because the body HMAC passed.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook, capturing the raw body `B` and the `X-Shopify-Hmac-Sha256` header `H` (valid because `H = HMAC(api_secret_key, B)`).
2. Attacker sends a new HTTP request to the app's webhook endpoint with the same body `B` and same `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares to `H` -- it matches, since neither depends on the shop header: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, so the app processes attacker-controlled/replayed body content as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
