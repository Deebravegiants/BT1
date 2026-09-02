## Title
Webhook HMAC only covers the request body, not the `shop`/`topic` identity headers, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — which are read straight from HTTP headers and then trusted as the tenant/event identity for the handler — are never included in the signed material. Anyone who can obtain a single valid `(body, hmac)` pair for an app (e.g., a merchant who has installed the app on their own store and receives one real webhook) can replay that same body/HMAC to the app's public webhook endpoint while freely rewriting the `shop-domain` and `topic` headers to any other value, since those fields are not bound by the signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC purely from `to_signable_string` and compares it to the `hmac` field: [2](#0-1) 

But `Registry.process` trusts `request.topic` and `request.shop` — both parsed from unauthenticated headers — to dispatch to a handler and to identify the tenant in `WebhookMetadata`: [3](#0-2) 

`shop`, `topic`, `webhook_id`, and `api_version` are all extracted straight from headers with no cryptographic tie to the signed body: [4](#0-3) 

This is exactly the bug class described in the external report: a field that is *acted on* (the shop identity used to route/attribute the webhook) is not *covered by the HMAC* that is supposed to bind the request to a specific, legitimate sender. The binding that should hold is:
`hmac_valid(raw_body) == true` should imply `shop header == the shop that actually generated this signed body`. In this implementation that equality does not hold — the HMAC only proves "this body was produced by someone holding `api_secret_key`" but says nothing about which shop or topic it belongs to.

Critically, `api_secret_key` is a single value shared across **all** shops/tenants that have installed a given app — it's not shop-specific. So any one of an app's many merchants (an "unprivileged" actor relative to other tenants) can trivially obtain a valid `(raw_body, hmac)` pair by triggering a real webhook event on their own store, then resend an HTTP POST directly to the app's public webhook endpoint with that same body/HMAC but with `shopify-shop-domain` (and/or `shopify-topic`) headers rewritten to target a different merchant/topic. The HMAC check still passes because it only ever validated the body.

### Impact Explanation
This breaks the tenant boundary the HMAC check is meant to enforce: a request that should only be attributable to "shop A, topic X" can be relabeled and processed by the host application as "shop B, topic Y" while still passing signature verification. Depending on how the host application uses `WebhookMetadata#shop`/`#topic` (e.g., to look up a session, update tenant-scoped data, or trigger app/uninstall/GDPR-style flows), this enables cross-tenant data confusion/corruption — one merchant forging webhook "events" attributed to another merchant's shop. This falls under the "cross-tenant access" High/Critical impact class.

### Likelihood Explanation
Likelihood is significant for multi-tenant apps: obtaining one legitimate `(body, hmac)` pair requires nothing more than being any ordinary merchant using the app (install the app on a free/dev store, trigger any webhook event). Constructing the forged request only requires rewriting HTTP headers, which is trivial and does not require access to `api_secret_key`, any access token, or any other credential.

### Recommendation
Include the identity-relevant fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for `to_signable_string`, or otherwise cryptographically bind them to the payload before computing/verifying the HMAC, so that the signature attests to the full event identity and not just the raw body bytes.

### Proof of Concept
1. As merchant A, install the app on a test store and trigger any webhook (e.g., `products/create`). Capture the raw POST body and the `x-shopify-hmac-sha256` header — this is a valid `(body, hmac)` pair for the app's shared `api_secret_key`.
2. Send a new HTTP POST to the app's webhook endpoint with the same body and `x-shopify-hmac-sha256` value, but set:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: <any topic the app has a handler for>`
3. `HmacValidator.validate` (per `lib/shopify_api/utils/hmac_validator.rb`) verifies successfully because it only checks the body against the HMAC.
4. `Registry.process` (per `lib/shopify_api/webhooks/registry.rb`) dispatches the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and `topic` set to the attacker-chosen value, even though the payload never actually originated from that shop/topic.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
