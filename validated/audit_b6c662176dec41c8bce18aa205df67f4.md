### Title
Webhook shop/topic identity spoofing via unsigned headers — HMAC only covers request body ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` and the `topic` from HTTP headers, but its HMAC-signable representation (`to_signable_string`) is only the raw request body. `Utils::HmacValidator.validate` therefore proves nothing about the `X-Shopify-Shop-Domain` or `X-Shopify-Topic` headers — only that the body bytes were signed with the app's `client_secret` at some point, for some shop. This breaks the identity binding `shop_verified == shop_used_by_handler`, allowing a malicious but legitimately-installed merchant to replay a genuinely-signed webhook body while spoofing the `shop` header to impersonate a different tenant.

### Finding Description
`Webhooks::Registry#process` authorizes and dispatches a webhook purely based on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the `hmac` field: [2](#0-1) 

But for webhook requests, `to_signable_string` is defined as just the raw body — it does **not** include `shop`, `topic`, or any other header: [3](#0-2) 

Meanwhile `shop` and `topic`, which are subsequently trusted and forwarded to the app's handler as the tenant identity for the event, are parsed straight from unauthenticated headers (`shopify-shop-domain`, `shopify-topic`): [4](#0-3) 

Since a single app-level `client_secret` signs webhooks for *every* shop that installs the app (there is no per-shop secret), any merchant who installs the app on their own store receives webhook deliveries whose body HMAC is valid under the app's shared secret. That merchant can then resend the exact same signed body to the app's webhook endpoint while substituting a different value in `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`). `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry#process` will hand the forged `shop` value straight to the handler via `WebhookMetadata`: [5](#0-4) 

This is the exact bug class from the external report: a value acted upon (`shop`/`topic`) is not covered by the integrity check (`hmac` over body only), so the "verified" and "used" identities diverge.

### Impact Explanation
An attacker (any developer who can create a free Shopify development store and install the target's public app) can inject data or trigger app logic that appears to originate from a victim shop that also has the app installed, without ever possessing the victim's access token or the app's `client_secret`. Depending on how the host app's webhook handlers key data by `shop`, this can corrupt or overwrite another tenant's stored state (orders, customer data, uninstall/GDPR handlers, etc.), i.e., cross-tenant access/data confusion — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Moderate-to-high: no leaked credentials, TLS interception, or privileged account is required — only a standard, free Shopify store installation of the target app, which is available to any unprivileged internet user. The only extra step is capturing one's own genuinely-delivered webhook body and replaying it with a modified `shop`/`topic` header, both trivial for anyone who can install the app.

### Recommendation
Include `shop` (and ideally `topic`) in the signable content verified against the HMAC, or require the host application to cross-check `request.shop` against a known/installed-session registry before trusting it as the tenant identity, rather than relying solely on body-HMAC validity.

### Proof of Concept
1. Install the target app on an attacker-controlled Shopify dev store (`attacker.myshopify.com`), triggering Shopify to send a real webhook (e.g., `orders/create`) with a valid `X-Shopify-Hmac-Sha256` signed over the raw body using the app's `client_secret`.
2. Capture the raw body and its valid HMAC header.
3. Replay the identical raw body and HMAC to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (a known real merchant of the same app) and/or a different `X-Shopify-Topic`.
4. `ShopifyAPI::Webhooks::Registry#process` calls `Utils::HmacValidator.validate(request)`, which passes because `Request#to_signable_string` only checks `@raw_body` — the spoofed `shop`/`topic` headers are never validated: [6](#0-5) 
5. The handler executes with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` believing the event legitimately belongs to `victim-shop.myshopify.com`.

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
