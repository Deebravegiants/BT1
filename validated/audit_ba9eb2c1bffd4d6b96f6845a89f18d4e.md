### Title
Webhook Shop/Topic Identity Is Not Bound to the HMAC Signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` authenticates a webhook delivery by validating an HMAC over the raw request body only, but the `shop`, `topic`, and `webhook_id` values that the registry trusts as the *identity* of the event are taken from unauthenticated HTTP headers that are never included in the signed material. This breaks the binding `HMAC-authenticated bytes == bytes used to identify the tenant (shop)`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `HmacValidator.validate` computes/compares the signature exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic tie to the signature: [3](#0-2) 

`Registry.process` validates only the HMAC and then unconditionally trusts these header-derived fields to route and label the event to the handler: [4](#0-3) 

Because the HMAC key (`Context.api_secret_key`) is the app's single client secret shared across *every* shop that has installed the app, any merchant that has installed the app can trivially obtain a valid `(raw_body, hmac)` pair by triggering a real webhook on their own store. That pair remains valid for **any** value of the `shop-domain`, `topic`, and `webhook-id` headers, because those headers are never part of the signed string. An attacker can therefore replay the captured body+hmac to the app's public webhook endpoint while substituting the victim's `shop-domain` header (and/or a different `topic`), and `Utils::HmacValidator.validate` will still return `true`, letting `Registry.process` hand the forged `WebhookMetadata` (with the victim's `shop`) to the handler.

This is the same class of bug as the reported issue: the report shows that `LineaProofHelper.verifyAccountProof` proves proof integrity but never checks that the proven account `key` equals the actual `target` address used for the fetch — i.e., verified bytes ≠ bytes used for identity. Here, the verified bytes (`raw_body`) are likewise disconnected from the bytes used for tenant identity (`shop`, `topic`, `webhook_id` headers).

### Impact Explanation
This allows cross-tenant spoofing of webhook events: an attacker-controlled merchant account can forge a webhook that the host application believes originates from a different, victim shop. Depending on how the hosting application's webhook handler acts on `WebhookMetadata#shop` (e.g., updating billing/subscription state, processing `shop/redact`, `customers/redact`, `customers/data_request`, or `app/uninstalled`-type flows keyed by shop), this can result in cross-tenant data corruption, spurious GDPR redaction against a victim shop, or other tenant-confused state changes — a cross-tenant integrity/access violation.

### Likelihood Explanation
Exploitation only requires the attacker to control (or install the target app on) at least one shop to obtain one valid `(body, hmac)` pair signed with the shared `client_secret`; no access to the victim's credentials, access token, or `client_secret` is needed. Replaying that pair to the app's public webhook endpoint with a modified `shop-domain`/`topic` header is trivial once the pair is obtained, since none of those headers are covered by the signature check in `Utils::HmacValidator.validate`.

### Recommendation
Include the shop domain, topic, and webhook id in the signable string (or otherwise cryptographically bind them, e.g. by validating `request.shop` against a shop-scoped secret or session known to the app) so `to_signable_string` in `lib/shopify_api/webhooks/request.rb` covers all fields the application relies on for identity, not just the raw body. At minimum, document that host applications must independently verify `request.shop`/`request.topic` against known/installed shops, since the gem's HMAC check does not cover them.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the raw request body `B` and the valid `x-shopify-hmac-sha256` header `H` computed by Shopify using the app's shared `client_secret`.
2. Attacker POSTs to the app's public webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and/or a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which passes, because validation only checks `raw_body` against `H`: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, even though the event never originated from the victim's store.

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
