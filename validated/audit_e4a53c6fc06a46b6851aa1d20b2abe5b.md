### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain`, `topic`, and `webhook-id` values taken from HTTP headers when constructing the `WebhookMetadata` passed to the app's handler. None of these header-derived identity fields are part of the signed payload, so they can be freely substituted by anyone who can produce one valid `(raw_body, hmac)` pair for the shared app secret.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are all read directly from HTTP headers and are never part of the signable string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)` (which HMACs `to_signable_string`, i.e. the body only) and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the metadata handed to the app's registered handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field — for a `Request` this is exclusively the raw body: [4](#0-3) 

This is the exact bug class from the report generalized to identity binding: the equality the code *should* enforce is `hmac == HMAC(secret, body ‖ shop ‖ topic ‖ webhook_id)`, but the equality it *actually* enforces is `hmac == HMAC(secret, body)`, while `shop`/`topic`/`webhook_id` are "acted on but not covered by the HMAC." Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` deliberately includes `shop` in the signed parameters: [5](#0-4) 

showing the library's own established pattern is to bind tenant-identifying fields into the signature — a pattern the webhook path fails to follow for `shop`.

Because a single app-level `api_secret_key` is shared across every merchant/tenant that installs the app, any merchant who installs the app receives genuine webhooks with a valid `(body, hmac)` pair signed under that same shared secret. Nothing in `HmacValidator` or `Registry.process` ties that valid signature to the specific `shop-domain` header it originally arrived with.

### Impact Explanation
An attacker who controls one tenant (a shop with the app installed) can capture a legitimate webhook delivery (valid `raw_body` + `hmac`) and resend it to the app's webhook endpoint with the `shopify-shop-domain` (and optionally `shopify-topic` / `shopify-webhook-id`) headers rewritten to reference a different, victim shop. `HmacValidator.validate` will still pass because it only checks the body's HMAC, and `WebhookHandler#handle` will receive a `WebhookMetadata` claiming the event belongs to the victim shop. Any host application that uses `data.shop` (the standard, documented field) to look up the tenant's session/record to update will act on the victim's tenant using attacker-supplied body content — a cross-tenant data confusion/injection primitive. This satisfies the "cross-tenant access" Critical impact bucket, since the tenant boundary (`shop`) that the gem hands to the app is not authenticated.

### Likelihood Explanation
Any merchant that installs the target app can trivially obtain at least one valid `(body, hmac)` pair from their own legitimate webhook traffic (no secret material needed), and only needs to replay it with a modified `shop-domain` header, which requires no privileged access, no leaked credentials, and no interaction with Shopify's platform beyond normal app installation. This is a low-effort, directly reachable path through the gem's own webhook verification code (`Registry.process` / `Request` / `HmacValidator`), not a defect in a third-party dependency or a documented-API-ignoring host misuse.

### Recommendation
Bind the tenant-identifying headers into the HMAC computation (or otherwise cryptographically associate them with the verified body), mirroring the approach already used for OAuth's `AuthQuery`. At minimum, `Request#to_signable_string` should incorporate `shop`, `topic`, and `webhook_id` so that `HmacValidator.validate` fails if any of these are altered relative to what Shopify originally signed, or the gem should separately verify that the `shop-domain` header matches an expected/allow-listed shop before constructing `WebhookMetadata`.

### Proof of Concept
1. App is installed on attacker's own shop `attacker.myshopify.com` and on victim shop `victim.myshopify.com`, both webhooks signed with the same app `api_secret_key`.
2. Attacker triggers/receives a legitimate webhook on their own shop, capturing `raw_body` and the valid `shopify-hmac-sha256` header.
3. Attacker POSTs to the app's webhook endpoint with the captured `raw_body` and `hmac` unchanged, but sets `shopify-shop-domain: victim.myshopify.com` (and `shopify-topic`/`shopify-webhook-id` as desired).
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC: [6](#0-5) 
5. The app's handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: attacker_controlled_body, ...)` and, following the documented API, performs the corresponding tenant-scoped operation for `victim.myshopify.com` using attacker-supplied data.

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
