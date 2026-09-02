### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only signs the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `Utils::HmacValidator` only authenticates the JSON body of a webhook delivery. `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read straight from HTTP headers that are never included in the signed payload, then handed unmodified to the app's handler via `WebhookMetadata`.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it with the `hmac` field [1](#0-0) . For webhook requests, `to_signable_string` is defined as simply the raw request body [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly out of the `x-shopify-*`/`shopify-*` headers with no cryptographic binding to those header values [3](#0-2) .

`Registry.process` only checks that the HMAC over the body is valid, then immediately trusts `request.shop` (and the other header-derived fields) to build the `WebhookMetadata` passed to the app's registered handler [4](#0-3) . Because `api_secret_key` is the app's single client secret shared across every shop that has installed the app (it is not per-shop), a valid HMAC only proves "this body was signed by Shopify for this app" — it does **not** prove which shop the body belongs to.

The broken identity binding is:
`shop value trusted by the handler (Request#shop, from the "shop-domain" header)` ≠ `shop value actually covered by the HMAC (none — to_signable_string only contains the body)`.

An attacker who controls their own (self-service) Shopify shop can:
1. Trigger a legitimate webhook delivery to the app (valid HMAC, valid body, correct `shop-domain: attacker-shop.myshopify.com`).
2. Capture that delivery and replay the identical body + HMAC to the app's webhook endpoint, but with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a victim shop's domain.
3. Since the HMAC never covered the header, `Utils::HmacValidator.validate` still succeeds, and `Registry.process` calls the handler with `WebhookMetadata#shop` equal to the victim's shop while `WebhookMetadata#body` is fully attacker-controlled content.

Any host app that uses `data.shop` from the handler to key per-tenant storage, look up/attach an access token, or otherwise scope multi-tenant data will attribute attacker-controlled payload contents to the wrong tenant.

### Impact Explanation
This is a cross-tenant identity-confusion primitive: an unprivileged, self-registered Shopify merchant can make the app believe attacker-supplied webhook data originated from a different, victim shop, since the shop identity is never bound to the signed content. Depending on how the host app processes `WebhookMetadata#shop`, this can lead to cross-tenant data poisoning/access, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only an ordinary self-service Shopify account (attacker's own shop) to capture one legitimate, validly-signed webhook and replay it with a modified header — no access to the app's `client_secret`, access tokens, or any privileged account is required.

### Recommendation
Include the shop domain (and ideally the topic/webhook id) inside the HMAC-signed content, or otherwise cryptographically bind them (e.g., verify the header-supplied `shop` against a shop that is independently known to be associated with the delivery, or use Shopify's newer signed webhook mechanisms) instead of trusting `Request#shop`/`#topic`/`#webhook_id` purely from unauthenticated headers in `lib/shopify_api/webhooks/request.rb`.

### Proof of Concept
1. Register a webhook handler in the host app that uses `WebhookMetadata#shop` to select per-tenant storage/credentials.
2. As an attacker with your own Shopify dev/trial shop, trigger a webhook (e.g. `orders/create`) to capture `{raw_body, x-shopify-hmac-sha256}` — both valid.
3. POST this same `raw_body` (unchanged, so HMAC still validates) to the app's webhook endpoint, replacing `x-shopify-shop-domain` with the victim shop's domain.
4. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC successfully (`Utils::HmacValidator.validate`) and invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_controlled_json, ...)` [5](#0-4) , demonstrating the shop/body mismatch reaches the app layer unchecked.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
