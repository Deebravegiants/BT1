### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` (and `topic`) values used downstream to attribute and process the webhook are taken from unauthenticated HTTP headers. This mirrors the "field acted on but not covered by the HMAC" bug class from the referenced report: a value that drives business logic is not bound to the same authentication check that is supposed to prove message integrity/origin.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from HTTP headers, with no cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the HMAC of the signable string (`raw_body`) matches; it never verifies that `shop` or `topic` are part of the signed content: [3](#0-2) 

`Registry.process` accepts the request once `HmacValidator.validate` passes, then dispatches the handler using the unauthenticated `request.shop` and `request.topic`, treating them as trusted tenant identity: [4](#0-3) 

Critically, the HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across *every* shop that has installed the app — it is not shop-specific. Any merchant that installs the app is, from Shopify's own webhook delivery system, a legitimate holder of validly-HMAC'd payloads (Shopify signs the webhooks it sends to that merchant's endpoint using the same app secret). Because the `shop-domain` header is excluded from the signable string, an attacker who controls their own shop installation can:

1. Trigger a webhook to their own store (e.g., `orders/create` with attacker-chosen body content), receiving a request with a valid `hmac-sha256` header signed by the shared `api_secret_key`.
2. Replay that exact `raw_body` + `hmac-sha256` value to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain.
3. `Utils::HmacValidator.validate` still succeeds because it only checks `raw_body` against the HMAC — it never re-derives or checks `shop`.
4. `Registry.process` calls `handler.handle` with `shop: request.shop` set to the victim's domain, causing the app to process attacker-controlled webhook data as if it originated from — and pertains to — the victim's shop.

Formally, the broken identity binding is:
`HMAC(api_secret_key, raw_body) == received_hmac` is verified, but `shop_header == shop_that_actually_sent_the_request` is never checked, even though `shop_header` is used as the tenant key for all downstream processing.

### Impact Explanation
This breaks the tenant isolation the HMAC check is meant to provide. A malicious app-installing merchant (unprivileged with respect to other tenants of the same app) can inject arbitrary, validly-signed webhook payloads under a victim shop's identity, since `shop-domain` is not bound to the signature. Depending on how the host application's webhook handlers use `WebhookMetadata#shop` (e.g., to look up which merchant's data/session to mutate), this enables cross-tenant data corruption or state confusion — matching the "cross-tenant access" impact category, as the attacker forces the app to attribute crafted webhook content to a shop they do not control.

### Likelihood Explanation
Exploitability requires only an app installation on any shop (a normal, unprivileged action for any Shopify merchant) plus the ability to intercept/replay one legitimately delivered webhook and modify the `shop-domain` header when re-POSTing it to the app's public webhook endpoint. No access token, session, or elevated privilege is required — only participation as a regular app-installing merchant, which satisfies the "unprivileged internet user" threat model.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signed content that `HmacValidator` verifies, or otherwise cross-validate `request.shop` against a shop known to have installed the app for that specific delivery (e.g., validate against Shopify's `X-Shopify-Webhook-Id` uniqueness combined with a shop-scoped secret, or require verification that the webhook actually belongs to the shop claimed, via a server-side registration lookup) instead of trusting the header value directly for tenant attribution.

### Proof of Concept
1. Install the target app on `attacker.myshopify.com`.
2. Trigger any webhook topic subscribed by the app (e.g. `orders/create`) so Shopify delivers a request such as:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of raw_body signed with shared api_secret_key>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id": 1, "malicious": "payload"}
   ```
3. Capture this request, then replay it to the app's public webhook endpoint, only changing:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request; `Utils::HmacValidator.validate` succeeds because `to_signable_string` (`raw_body`) and `hmac-sha256` are unchanged.
5. `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host application to process the attacker's payload as though it were sent by/for `victim.myshopify.com`.

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
