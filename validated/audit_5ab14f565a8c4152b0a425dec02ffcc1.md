## Title
Webhook shop identity is not bound by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read from separate, unsigned HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that the HMAC matches the raw body, then trusts `request.shop` as the tenant identifier passed to the app's webhook handler. This breaks the intended binding: `shop header == shop bound by HMAC`. In reality, `shop header != HMAC-covered data`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` (and `topic`/`webhook_id`/`api_version`) accessors read from HTTP headers that are never included in that signable string: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only checks `request.hmac` against `compute_signature(request.to_signable_string, secret)` — i.e., against the raw body — and then immediately trusts `request.shop` to construct the tenant-scoped `WebhookMetadata` handed to the app's handler: [3](#0-2) [4](#0-3) 

Because the HMAC only binds the body bytes and not the `shop-domain` header, any request bearing a body/HMAC pair that is valid for *some* shop will also pass validation with the `shop-domain` header changed to any other value — the signature check cannot detect the substitution.

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler receives `WebhookMetadata` with an attacker-chosen `shop` value while the HMAC only proves the body came from a legitimate Shopify secret holder for *some* shop, not that specific one. Any app logic that trusts `data.shop` to select which tenant's records to create/update/delete (order data, fulfillment status, inventory, GDPR data-request handling, etc.) can be made to attribute or apply data intended for shop A to shop B, i.e., cross-tenant access/data corruption — meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
An attacker needs one legitimate (body, HMAC) pair for the app's own secret — obtainable by installing the app on their own store (a real Shopify merchant account, not a privileged internal credential) and capturing one of their own delivered webhooks, or observing a webhook they legitimately receive. They then replay that same body/HMAC to the app's public webhook endpoint while altering the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to a victim shop domain. No `api_secret_key`, access token, or Shopify-side compromise is required — only knowledge of the header names and the gem's documented delivery format, both public.

### Recommendation
Bind the tenant-identifying fields into the signed payload, or otherwise cryptographically bind the `shop` header to the signature before trusting it — e.g., compute/verify the HMAC over `shop + topic + webhook_id + raw_body` (matching what Shopify actually signs, if Shopify includes headers in its HMAC, or otherwise require out-of-band confirmation that `request.shop` corresponds to a shop with an active app installation/session before dispatching to handlers). At minimum, `Registry.process` should cross-check `request.shop` against a known/authorized shop list (e.g., an existing session for that shop) rather than trusting the header outright.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the raw request: headers (`x-shopify-topic`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker.myshopify.com`, ...) and raw body.
2. Replay the exact same raw body and HMAC header to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the raw body against the HMAC.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and invokes the app's handler, which now processes/attributes the attacker's payload as belonging to the victim shop.

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
