This confirms the finding: `WebhookMetadata.shop` (used by app developers to identify which merchant a webhook belongs to) is populated straight from `Request#shop`, i.e. the `x-shopify-shop-domain`/`shopify-shop-domain` header, while `Utils::HmacValidator.validate` only authenticates `Request#to_signable_string`, which returns solely `@raw_body`. The `shop` header therefore travels outside the cryptographic envelope. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating `Utils::HmacValidator.validate(request)`, which checks the `X-Shopify-Hmac-Sha256` signature strictly against the raw request body. The `shop` value that identifies *which merchant/tenant* the webhook is about is read from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header and passed unchanged into `WebhookMetadata#shop`, which host applications use to route/act on the corresponding tenant's data. Because the shop header is never included in the signed material, an attacker who controls a valid HMAC/body pair (trivially obtainable by installing the app on their own store and capturing a genuine webhook delivery) can replay the identical body+HMAC while substituting an arbitrary `x-shopify-shop-domain` header, and the signature check still succeeds.

### Finding Description
The security guarantee an app developer relies on is: `hmac valid` ⇒ `(body, shop)` pair is authentic and was sent by Shopify for that shop. The gem only proves `hmac valid` ⇒ `body` is authentic; it makes no assertion about `shop`. Concretely:

- `Request#hmac` decodes the `hmac-sha256` header.
- `Request#to_signable_string` returns only `@raw_body`.
- `HmacValidator.validate_signature` computes `HMAC(secret, to_signable_string)` and compares it with the received signature — the `shop` header is completely outside this computation.
- `Registry.process` only calls `Utils::HmacValidator.validate(request)` before invoking the handler with `WebhookMetadata.new(topic:, shop: request.shop, body:, ...)`.

Since Shopify signs webhooks using the app's single shared `client_secret` (not a per-shop secret), any merchant that has installed the app can capture a legitimately-signed webhook for their own shop and then re-send it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. The HMAC still validates because it never covered that header, so `Registry.process` calls the developer's handler believing the event pertains to the victim shop.

### Impact Explanation
This breaks the tenant-isolation identity binding the library is supposed to enforce (`hmac-authenticated shop == acting shop`), letting an unprivileged app-installing attacker inject fabricated events attributed to any other shop that also uses the app. Depending on how the host app's webhook handlers act on `data.shop` (e.g., toggling shop settings, uninstall/redact flows, updating shop-scoped records, revoking access, writing shop-scoped billing/subscription state), this can cause cross-tenant data corruption or unauthorized cross-tenant actions — matching the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on their own Shopify store (a normal, unprivileged action available to any merchant) to obtain one authentic `(body, hmac)` pair, then replay it with a modified shop header value against the app's public webhook endpoint. No access to the app's `client_secret`, no access token, and no privileged account is required — matching the required "unprivileged internet user" threat model.

### Recommendation
Bind the shop identity into the signed material or otherwise cryptographically verify it before trusting `request.shop`:
- Include the `shop` (and ideally `topic`/`webhook_id`) in `to_signable_string`, or
- Cross-check `request.shop` against a shop-to-installation record (e.g., verify the shop has an active session/access token that was itself obtained via authenticated OAuth/token-exchange) before acting on the webhook, and reject/flag mismatches, or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be independently validated by the host application against its own installation records before being trusted.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `app/uninstalled` or any topic the developer's handler treats as sensitive).
2. Shopify delivers a genuine webhook to the app's endpoint:
   ```
   POST /webhooks
   x-shopify-topic: some/topic
   x-shopify-hmac-sha256: <valid HMAC of raw body with app's client_secret>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"...": "..."}
   ```
3. Attacker captures this exact `body` + `x-shopify-hmac-sha256` value, then re-sends it to the same endpoint, only changing the shop header:
   ```
   POST /webhooks
   x-shopify-topic: some/topic
   x-shopify-hmac-sha256: <same valid HMAC as captured>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: <identical body>
   ```
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) computes the HMAC over `@raw_body` only (`lib/shopify_api/webhooks/request.rb:35-38`) and finds it matches — validation succeeds.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the developer's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to act as if `victim-shop` sent this webhook, even though it never did.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
