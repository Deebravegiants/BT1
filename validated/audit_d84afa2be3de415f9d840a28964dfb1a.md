### Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw HTTP body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` as the tenant identity passed to the app's webhook handler, breaking the binding `shop authenticated by HMAC == shop used to identify the tenant`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are pulled straight from headers that are never included in the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (the raw body) against the app's `Context.api_secret_key`: [3](#0-2) 

`Registry.process` checks that HMAC and, once it passes, dispatches to the handler using `request.shop` (and `request.topic`) taken directly from the unauthenticated headers: [4](#0-3) 

Because Shopify signs webhooks with the app's single `client_secret` (the same secret used for every shop that installs the app), any shop that has installed the app can legitimately receive a validly-signed webhook body/HMAC pair from Shopify. Nothing prevents that body+HMAC pair from being replayed to the app's webhook endpoint with the `shop-domain` (and/or `topic`/`webhook-id`) header rewritten to a different, victim shop domain: the HMAC still validates because it is computed only over the raw body, which is unchanged. `Registry.process` then calls the app's handler with `WebhookMetadata.shop` set to the attacker-chosen value, so the app processes/attributes a legitimate event body under an arbitrary tenant identity of the attacker's choosing.

This is directly analogous to the reported bug class of "a field acted on but not covered by the HMAC" causing an identity-binding break — here it is the `shop` field used for tenant attribution rather than a numeric cast, but the root cause (trusting an unauthenticated field alongside an authenticated one) is the same pattern.

For comparison, the OAuth callback verifier (`AuthQuery`) does this correctly by including `shop` and `host` inside the signed string: [5](#0-4) 

### Impact Explanation
An attacker who controls one shop that has the app installed can cause the app's webhook handler to process events under an arbitrary victim shop's identity (cross-tenant spoofing), because tenant attribution (`shop`) is not bound to the HMAC that Shopify computes. This can lead the host application to write/act on data under the wrong tenant, satisfying "cross-tenant access" impact criteria.

### Likelihood Explanation
Exploitation requires only that the attacker's own shop have the app installed (an unprivileged, self-serve action for any Shopify merchant) and the ability to replay/re-POST an HTTP request with a modified header to the app's public webhook endpoint — no access to `api_secret_key`, access tokens, or the victim's credentials is needed, since the shared app secret signs the (unmodified) body regardless of which shop it nominally came from.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values in the signed/verifiable content, or otherwise cryptographically bind the shop domain to the payload before trusting it, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop`/`host` in the HMAC input. At minimum, `Registry.process` should not rely on unauthenticated headers for tenant identification without an additional binding check (e.g., verifying the shop against a known/registered installation) before invoking the handler.

### Proof of Concept
1. App is installed on attacker-controlled shop `attacker.myshopify.com`; Shopify sends a legitimately signed webhook (`body`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker.myshopify.com`) to the app's webhook endpoint.
2. Attacker intercepts/replays this exact request but rewrites the `x-shopify-shop-domain` header to `victim.myshopify.com` (and/or `x-shopify-topic`), leaving the raw body untouched.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which passes because it only checks the HMAC over the unmodified raw body: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, so the app processes the event as if it originated from the victim shop.

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
