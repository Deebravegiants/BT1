### Title
Webhook `shop`, `topic`, and `webhook-id` fields are trusted by `Registry.process` without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used later to identify the request are parsed unauthenticated from HTTP headers. Because the gem's `Registry.process` dispatches to a handler and constructs `WebhookMetadata` using these header-derived, unsigned values, an attacker who owns any shop that has installed the app can capture one of their own legitimate, correctly-HMAC-signed webhook deliveries and replay it to the same endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header. The HMAC check still passes because it only verifies the body bytes, but the host application's handler receives attacker-controlled shop/topic identity, breaking the binding between "the shop that produced this signed payload" and "the shop the application believes sent it."

### Finding Description
`to_signable_string` for the webhook request is defined as just the raw body: [1](#0-0) 

`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, to_signable_string)` and compares it to the `hmac` field: [2](#0-1) 

Neither `topic`, `shop`, `webhook_id`, nor `api_version` are included in the signed content — they are read directly from (attacker-controllable, at the HTTP layer) headers: [3](#0-2) 

`Registry.process` validates the HMAC over the body, then uses these *unsigned* header-derived values to select the handler and populate the metadata handed to the application: [4](#0-3) 

Since a given app has a single `client_secret` shared across every shop that installs it (this is normal for Shopify apps, not a privileged secret specific to one merchant), any unprivileged user who installs the app on their own store will receive genuine webhooks that are validly HMAC-signed with that shared secret over the body. That attacker can then replay the exact same `(raw_body, hmac)` pair to the app's webhook endpoint while substituting a different value for `X-Shopify-Shop-Domain` (claiming to be a victim shop that also uses the app) and/or `X-Shopify-Topic`. `HmacValidator.validate` will accept the replayed payload because it never inspected those headers, and `Registry.process` will pass the attacker-chosen `shop` value straight into `WebhookMetadata`, which the host application uses to attribute the event, look up shop-scoped records, or make business decisions.

This is the exact class of bug described in the reference report: a value that is *acted upon* (here, `shop`/`topic`, used to route and attribute the webhook) is not covered by the integrity check (the HMAC), producing a mismatch between "the identity the signature actually vouches for" (none — only the body) and "the identity the application trusts" (the header value).

### Impact Explanation
This breaks the binding `shop_that_signed_the_payload == shop_the_application_processes_it_as`. An attacker with a normal, unprivileged Shopify store that has the target app installed can forge webhook attribution for any other shop using the same app, without needing the app's `client_secret`, an access token, or any other privileged credential — only replay of their own legitimately received webhook with modified headers. Depending on how the host app's webhook handler consumes `WebhookMetadata#shop` (e.g. writing/deleting shop-scoped data, triggering `customers/redact` or `shop/redact` type flows, updating billing/plan state), this enables cross-tenant data corruption or unauthorized actions attributed to a victim shop — a cross-tenant boundary violation stemming directly from this gem's `Webhooks::Request`/`Registry` implementation.

### Likelihood Explanation
Likelihood is high for any deployment that relies on this gem's webhook facilities as documented: creating a Shopify development store and installing the target app is unprivileged and free; capturing one's own webhook body+HMAC is standard operation; replaying an HTTP POST with a modified header requires no special access. No secrets, tokens, or social engineering are needed.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-covered signable content, or otherwise cryptographically bind them to the signed body (e.g., concatenate the header values with the raw body before computing/verifying the digest), matching how Shopify's own webhook signing actually authenticates the full delivery, not just the JSON payload bytes. At minimum, `Registry.process` should not trust `request.shop`/`request.topic` for dispatch/attribution unless those fields are also verified as originating from the same signed delivery.

### Proof of Concept
1. Attacker creates/owns Shopify store `attacker.myshopify.com` and installs the target app (any user can do this).
2. Shopify sends a legitimate webhook to the app's endpoint, e.g.:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-of-body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   X-Shopify-Webhook-Id: ...
   Body: {"id":123,...}
   ```
3. Attacker captures this exact `(body, hmac)` pair.
4. Attacker resends the same body/hmac to the same endpoint, but sets:
   ```
   X-Shopify-Shop-Domain: victim.myshopify.com
   ```
5. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only, finds it matches, and returns `true`.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb` lines 188-200) dispatches the handler with `shop: "victim.myshopify.com"` even though the payload never originated from, nor was ever seen by, that shop — a forged cross-tenant webhook event accepted as authentic.

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
