### Title
Webhook `shop-domain` header is trusted for dispatch despite not being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by checking only the raw request body against `X-Shopify-Hmac-Sha256`, then unconditionally trusts the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) headers when building the `WebhookMetadata` passed to the app's handler. Because those headers are not part of the signed bytes, any party who possesses one valid `(body, hmac)` pair — trivially obtainable by installing the app on their own shop and receiving a real webhook — can replay that exact body/HMAC pair while freely rewriting the `shop-domain` header to name a different (victim) shop.

### Finding Description
The HMAC binding for OAuth callbacks (`AuthQuery#to_signable_string`) explicitly signs `code`, `host`, `shop`, `state`, `timestamp` together, so the `shop` value is bound to the signature: [1](#0-0) 

But for webhooks, `Request#to_signable_string` only returns the raw body — none of the identifying headers are part of the signable content: [2](#0-1) 

The `shop`, `topic`, and `webhook_id` accessors read directly from attacker-controlled HTTP headers, independent of the signature: [3](#0-2) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (i.e. the raw body for webhooks) against the computed HMAC — it has no knowledge of, and does not include, any headers: [4](#0-3) 

`Registry.process` calls this HMAC check and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to construct the `WebhookMetadata` object dispatched to the registered handler: [5](#0-4) 

The identity binding that should hold is:
`HMAC_verified(bytes) == bytes_trusted_by_handler`

but instead:
`bytes_verified = raw_body` while `bytes_trusted_by_handler = raw_body ∪ {shop, topic, webhook_id}` — the shop-domain header is parsed and acted upon by the host application without ever being covered by the signature that is supposed to authenticate the request as coming from Shopify for that specific shop.

### Impact Explanation
Any attacker who has obtained one legitimately-signed `(raw_body, hmac)` pair — for example by installing the target app on a shop they control and receiving a real webhook delivery for that shop — can resend that identical body/HMAC to the app's public webhook endpoint while swapping in an arbitrary `X-Shopify-Shop-Domain` header naming a victim shop. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-supplied) body belongs to the victim shop. Any host application logic that persists, redacts, or actions data keyed by `WebhookMetadata#shop` (e.g. `customers/redact`, `shop/update`, `app/uninstalled` handling) can be tricked into applying attacker-chosen webhook content under a victim tenant's identity — a cross-tenant data/action confusion crossing the shop-authentication boundary this gem is meant to enforce.

### Likelihood Explanation
The webhook endpoint is by design public and unauthenticated at the transport level (Shopify calls it over plain HTTPS with only the HMAC header as proof of authenticity). Obtaining one valid signed payload requires nothing beyond installing the app on any shop (including a free/dev store) — no leaked secrets, no privileged access, and no dependency on host-application misconfiguration. This is squarely within reach of an "unprivileged internet user" analog described by the reference report: the code checks *that* the message is from Shopify, but not *for which shop* it was intended, exactly mirroring the killed-gauge report's "isGauge but not isAlive" pattern of checking a necessary but insufficient predicate.

### Recommendation
Include the trust-relevant webhook headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the bytes that are HMAC-verified, or otherwise cryptographically bind them to the signature (Shopify's own webhook signing does not natively include headers, so this may require rejecting/ignoring header-derived identity in favor of values embedded in the verified payload, or documenting prominently that consumers must not treat `WebhookMetadata#shop`/`#topic` as authenticated and must cross-check them against out-of-band registered subscription data). At minimum, `Registry.process` should validate that the `shop` supplied in headers corresponds to a shop with an active registration for that specific webhook/topic before dispatching to the handler, rather than blindly trusting the header value.

### Proof of Concept
1. Install the target app on `attacker.myshopify.com` (any dev store) and register the same topic (e.g. `orders/create`) the target app subscribes to.
2. Trigger the event on `attacker.myshopify.com` and capture the resulting HTTP webhook request Shopify sends to the app: note the `raw_body` and the `X-Shopify-Hmac-Sha256` header.
3. Replay that exact `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` returns `true` (it only hashes `raw_body`), so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) proceeds and calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)`, even though Shopify never sent this payload for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

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
