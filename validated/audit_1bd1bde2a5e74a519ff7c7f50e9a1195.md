### Title
Webhook shop/topic identity not covered by HMAC allows cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop`, `topic`, and `webhook_id` values taken from HTTP headers to route and label the payload. Because the HMAC signature never covers these header fields, the "shop" that is cryptographically verified and the "shop" that is acted upon by the host app are two different things, breaking the identity binding: `verified_bytes (raw_body) != identity_used (shop header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) 
`to_signable_string` returns only `@raw_body` — none of `shop`, `topic`, `webhook_id`, or `api_version` (all read straight from attacker-controlled HTTP headers) are part of the signed material: [2](#0-1) 

`Registry.process` validates only that the HMAC matches the raw body against the app's single shared `api_secret_key` (the same key is used for every shop/tenant the app serves), and then immediately trusts `request.shop` and `request.topic` to build the `WebhookMetadata` handed to the app's webhook handler: [3](#0-2) 

`Utils::HmacValidator.validate` performs no comparison against the claimed shop/topic — it just recomputes the HMAC of the signable string and compares it to the supplied `hmac`: [4](#0-3) 

Because `api_secret_key` is shared across every shop that installs the app, any party who can install the app on their own (e.g. free development) store can legitimately receive Shopify-signed webhook deliveries — i.e., they can obtain arbitrary `(raw_body, valid_hmac)` pairs signed with the app's own secret. Nothing in `Request` or `Registry.process` ties that signed body to the shop domain it originated from. An attacker can therefore replay a validly-signed body while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to any value, including a victim tenant's shop domain. `HmacValidator.validate` will still pass because it only checks the body signature, and `Registry.process` will invoke the app's handler with `shop: <attacker-chosen victim domain>` and forged `topic`/`body` content.

This exactly matches the bug-class pattern of "a field acted on but not covered by the HMAC": the `shop` field used by the handler for tenant identification is not the field verified by the HMAC.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` to look up the tenant's stored session/data (the documented and expected usage pattern shown throughout the gem's webhook docs/tests), an attacker can inject arbitrary attacker-controlled webhook content that is processed and stored under a victim shop's tenant record — a cross-tenant data-integrity/cross-tenant access issue. Depending on the handler's logic (e.g., updating order/customer/app-subscription state, revoking access, or triggering downstream actions "on behalf of" the victim shop), this can lead to cross-tenant data corruption or actions being taken against a tenant that never sent the webhook.

### Likelihood Explanation
Medium-to-High: exploitation requires only that the attacker be able to install the app on any shop under their control (a routine, unprivileged action for any Shopify developer/merchant) to obtain a validly-signed webhook body/HMAC pair, and then send that body with a forged shop header directly to the app's public webhook endpoint. No access to the victim's credentials, `api_secret_key`, or access tokens is required — only knowledge of the app's public webhook URL, which is typically discoverable.

### Recommendation
Bind the identity fields into the verified material instead of trusting unauthenticated headers:
- Include `shop`, `topic`, and `webhook_id` in the string that is HMAC-verified (Shopify's actual webhook signing only covers the body by design, so this cannot be "fixed" purely client-side); alternatively/additionally, cross-check the claimed `shop` header against a shop the app has an active, previously-established session/installation record for before processing, and reject webhooks whose claimed shop was not the shop actually registered to receive that specific webhook subscription/topic.
- Document prominently that `Request#shop`/`Request#topic` are NOT covered by the HMAC and must not be trusted as authoritative tenant identifiers without an independent installation/session check by the consuming application.

### Proof of Concept
1. Attacker installs the target app on their own (e.g., free/dev) Shopify store `attacker-shop.myshopify.com`, thereby causing Shopify to send legitimate, HMAC-signed webhook deliveries to the app's webhook endpoint using the app's shared `api_secret_key`.
2. Attacker captures one such delivery: raw body `B` and its valid signature `H = HMAC_SHA256(api_secret_key, B)` (headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: <topic>`).
3. Attacker crafts a new HTTP POST to the same webhook endpoint, reusing body `B` and signature header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` only (per `to_signable_string`) and finds it matches `H`, since the body wasn't changed — validation succeeds. [5](#0-4) 
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, causing the app to process attacker-controlled data under the victim's tenant identity.

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
