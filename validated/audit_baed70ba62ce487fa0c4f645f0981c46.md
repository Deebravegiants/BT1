## Title
Webhook `shop` (and topic/api_version) fields are not covered by the HMAC signature, letting a malicious app-installing shop forge cross-tenant webhook events - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the handler using the `shop`, `topic`, `api_version`, and `webhook_id` values taken from unauthenticated HTTP headers. Because those header fields are never included in the signed payload, any party capable of obtaining one valid `(raw_body, hmac)` pair signed with the app's `client_secret` — which every shop that installs the app can trivially obtain from its own legitimate webhook deliveries, since Shopify uses the same app-wide secret for every shop — can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header. The handler will process the forged event as if it originated from the spoofed shop.

### Finding Description
`Request#hmac` reads the HMAC from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors simply read separate, unauthenticated headers: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms only that the computed signature over `to_signable_string` (i.e., the raw body) matches the received HMAC — it never binds the `shop` header into the signed material: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to event by handler == shop cryptographically bound in the HMAC-covered payload`

In this implementation that equality does not hold: the HMAC only proves "this body was signed with the app's secret", not "this body came from shop X". Since Shopify signs webhooks for *all* shops of an app with the same `client_secret`, any shop that has installed the app can capture a legitimate `(body, hmac)` pair delivered to its own endpoint and resend it to the app's webhook endpoint with the `shop-domain` header rewritten to name a different (victim) shop. `Registry.process` will pass HMAC validation (since the body/HMAC pair is genuinely valid) and hand the app's handler a `WebhookMetadata` claiming the event is from the victim shop.

### Impact Explanation
This breaks tenant isolation: an unprivileged actor who legitimately installed the app on their own store can forge webhook events that the host application will process as if they came from another merchant's shop. Depending on how the host app's webhook handlers use `data.shop` (e.g., to look up/mutate shop-scoped records, trigger shop-scoped side effects, or index events), this enables cross-tenant data injection/corruption — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Any shop that installs the app receives real webhook deliveries and can capture arbitrary numbers of valid `(raw_body, hmac)` pairs at will. No access token, `client_secret`, or privileged access is required beyond normal use of the app. This makes exploitation straightforward for anyone who installs the app.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) header values into the signed material used for verification, e.g. by including the shop-domain header value in `to_signable_string`, or by requiring the host application to additionally verify that the webhook's `shop` matches a shop domain expected/registered for that specific HMAC-authenticated delivery before dispatching to handlers.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; trigger any event so Shopify delivers a webhook with headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`, and body `B`.
2. Replay a request to the app's webhook endpoint with the same body `B` and same HMAC header `H`, but with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, causing the host app to process/act on data or state keyed to `victim.myshopify.com` even though the payload actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
