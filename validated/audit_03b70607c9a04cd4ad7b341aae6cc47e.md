Confirmed root-cause facts:

- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, excluding every Shopify header — `topic`, `shop`, `api_version`, `webhook_id` are all read straight from HTTP headers, unauthenticated by the HMAC. [1](#0-0) 
- `Utils::HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, so it re-derives the HMAC solely from the body and never binds `shop`/`topic`. [2](#0-1) 
- `Registry.process` validates the HMAC and then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values taken straight from headers. [3](#0-2) 

### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated HTTP headers and passed unchecked into the handler. Any party who can obtain one valid `(body, hmac)` pair for a topic on a shop they control can replay that exact body/HMAC to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop, and the request still passes `HmacValidator.validate`.

### Finding Description
The identity binding that should hold is:
`shop authenticated by HMAC == shop the handler acts on`

In this gem it instead holds:
`bytes verified by HMAC (raw_body only) != bytes/headers the handler trusts (topic, shop, webhook_id, api_version)`

`Request#to_signable_string` returns `@raw_body` exclusively [4](#0-3) . `HmacValidator.validate_signature` recomputes the HMAC over that same signable string and compares it against the `hmac` header value using `OpenSSL.secure_compare` [2](#0-1) . Neither the shop domain nor the topic ever enters the signed material.

`Registry.process` only calls `HmacValidator.validate(request)` before dispatching to the registered handler using `request.topic`, `request.shop`, and `request.webhook_id`, all sourced from headers that are never part of the signature [5](#0-4) . Since any HTTP-reachable endpoint receives arbitrary headers from the caller (the host framework passes through whatever it received), an attacker who is an unprivileged user of the app for their own shop (e.g., they install/registered a webhook against their own dev store) can capture a legitimate `(raw_body, hmac)` pair emitted by a genuinely-signed webhook for their own tenant, then POST it directly to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns true because it only checks the body, and `Registry.process` will invoke the app's handler believing the event originates from the victim shop.

### Impact Explanation
This breaks the tenant-isolation boundary the gem is supposed to provide app authors: `Registry.process` is documented as the trusted gate that authenticates inbound webhooks before handing verified, shop-scoped data to app handlers. Because the shop/topic identity is not bound to the signature, an attacker can make the app believe a mandatory or app-lifecycle event (e.g. `app/uninstalled`, `shop/redact`, `customers/redact`) happened for an arbitrary victim shop, letting them trigger shop-scoped side effects (data deletion, deprovisioning, GDPR erasure flows, cache/state resets) for a tenant they do not own — a cross-tenant action forged with credentials belonging only to their own shop relationship with the app. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only: (1) install/register the app on an attacker-controlled shop to receive one genuinely HMAC-signed webhook — something any developer/merchant can do; (2) knowledge of the app's public webhook receiver URL, which is not secret; (3) ability to replay an HTTP POST with custom headers, which any unprivileged network client can do. No access token, `client_secret`, or privileged account is required, and several mandatory webhook topics (e.g. `shop/redact`) have small/fixed-shape bodies that are easy to obtain and replay verbatim.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material that `HmacValidator` checks, or otherwise cryptographically/architecturally bind the header-derived `shop`/`topic` values to the verified payload before they are used by `Registry.process`/handlers — e.g., have `Request#to_signable_string` incorporate the shop domain, or require host applications to bind the request to a session established independently of these headers before trusting `request.shop`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook for a topic with a small/fixed body (e.g. `app/uninstalled`).
2. Attacker uninstalls the app on their own shop, capturing the genuine webhook POST: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because Shopify signed it with the app's real `api_secret_key`).
3. Attacker sends a new POST directly to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only re-derives the HMAC from `B` [4](#0-3) .
5. `Registry.process` dispatches the handler with `shop: request.shop` equal to `victim-shop.myshopify.com` [6](#0-5) , causing the app to perform the "uninstalled"/data-redaction side effects for the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
