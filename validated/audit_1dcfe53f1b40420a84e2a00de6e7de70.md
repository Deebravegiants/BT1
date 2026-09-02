This confirms the finding: the docs explicitly tell developers to trust `ShopifyAPI::Webhooks::Registry.process` as verification "the request did indeed come from Shopify," and the `data.shop` field is documented as reliable webhook metadata, with no mention that `shop` is unauthenticated relative to the HMAC. Let me verify there's no other binding check I'm missing in `Registry.process` or `WebhookMetadata`.Confirmed: `Registry.process` only validates the HMAC over the raw body via `Utils::HmacValidator.validate(request)` [1](#0-0) , with no cross-check between `request.shop` and any signed value. This is sufficient to finalize the finding.

### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC verification, but the `shop` field used to attribute webhook data to a tenant is read directly from an unauthenticated HTTP header and is never bound to that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) . The `hmac` accessor decodes the `hmac-sha256` header and is checked against this same body-only string [3](#0-2) . Meanwhile `shop` is taken verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the body or the HMAC digest at all: [4](#0-3) .

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., the body signature) and then forwards `request.shop` straight into `WebhookMetadata` given to the app's handler as trusted tenant identity: [1](#0-0) . `HmacValidator.validate_signature` computes the digest solely from `verifiable_query.to_signable_string` (the body) and compares it via `OpenSSL.secure_compare`: [5](#0-4) . The `shop` header is never part of `to_signable_string`, so it is fully attacker-controllable independent of a valid HMAC.

Equality that should hold but doesn't: **shop bound by the signed bytes == shop reported to the handler**. Instead, only the request body is bound by the HMAC, while the `shop` field consumed by `WebhookMetadata.shop` is parsed straight from an unauthenticated header (`request.rb:20-23`), matching the "field acted on but not covered by the HMAC" class.

The docs reinforce that developers are expected to treat `Registry.process` as a full authenticity check ("This will verify the request did indeed come from Shopify") and treat `data.shop` as reliable tenant metadata, without any caveat that `shop` is excluded from the signature.

### Impact Explanation
Any party who possesses one legitimate `(raw_body, hmac)` pair signed with the app's `client_secret` — trivially obtainable by any merchant who installs the app and receives their own webhooks — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value naming a *different* merchant's shop. Because the HMAC only covers the body, verification succeeds, and the handler processes/stores the replayed body attributed to the victim shop. In a multi-tenant app that scopes data (orders, customer PII, GDPR redact requests, etc.) by `data.shop`, this enables cross-tenant data injection/corruption — writing or triggering actions against another merchant's tenant record using data the attacker fully controls (their own webhook body) but falsely attributed. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (1) the attacker to be an installed/authenticated merchant of the target app (to obtain a legitimate webhook body+HMAC of their own, or any means of observing one such pair), and (2) network access to POST to the app's public webhook endpoint with a modified `shop` header — no access token, `api_secret_key`, or privileged account needed beyond ordinary merchant self-service. This is a realistic, low-effort exploit path requiring no credential theft.

### Recommendation
Bind `shop` (and ideally `topic`, `webhook_id`) into the signed material, or have `Registry.process`/`WebhookMetadata` require the caller to independently verify that the `shop` header corresponds to a shop with an active installation/session before trusting it. At minimum, document prominently that `shop` in `WebhookMetadata` is not covered by the HMAC and must be cross-checked by the host application against known installed shops before being used for tenant-scoped operations.

### Proof of Concept
1. As a legitimate merchant of an app, capture one real Shopify webhook delivery: raw body `B` and header `shopify-hmac-sha256: H` (valid for `client_secret`).
2. Craft a new HTTP POST to the app's webhook endpoint with the same raw body `B` and header `shopify-hmac-sha256: H`, but set `shopify-shop-domain: victim-shop.myshopify.com` instead of the attacker's own domain.
3. Call:
```ruby
request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {
  "shopify-hmac-sha256" => H,
  "shopify-shop-domain" => "victim-shop.myshopify.com",
  "shopify-topic" => "orders/create",
})
ShopifyAPI::Webhooks::Registry.process(request)
```
4. `Utils::HmacValidator.validate(request)` returns `true` (per `lib/shopify_api/utils/hmac_validator.rb:26-31`, only body bytes are checked), and the registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though that shop never sent this webhook, demonstrating the spoofable tenant binding.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
