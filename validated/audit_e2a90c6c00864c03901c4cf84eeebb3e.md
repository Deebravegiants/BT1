### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from unsigned HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that the body's HMAC matches, then unconditionally trusts `request.shop` to attribute the event to a tenant. This breaks the intended binding: **shop identity used by the handler == shop identity actually authenticated by the HMAC**. In reality only the equality **HMAC-covered bytes (raw body) == bytes verified** holds; the `shop-domain` header is fully attacker-controllable while still passing validation.

### Finding Description
`to_signable_string` in `Request` returns just the raw body: [1](#0-0) 

`shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never mixed into the signable string: [2](#0-1) 

`Registry.process` validates the HMAC of the `Request` object (i.e., only the raw body) and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`, handing it to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms the signature over `verifiable_query.to_signable_string`, which for `Request` is solely `@raw_body`: [4](#0-3) 

Because the HMAC only binds the body, any two webhook deliveries that happen to carry the same body (e.g., an empty-body event, or any event with attacker-controlled/predictable body content) produce identical valid signatures regardless of which shop they were originally sent for. An attacker who installs the app on their own store (a normal, unprivileged action) can capture a Shopify-delivered webhook with a valid HMAC for a given body, then replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Registry.process` will accept it as valid and dispatch it to the handler tagged with the victim's shop, since nothing ties the header to the signed payload.

### Impact Explanation
This lets an attacker (any merchant who has legitimately installed the app, hence obtained at least one validly-signed webhook) inject events attributed to an arbitrary, unrelated shop into the host application's webhook handler. Depending on how the host app trusts `WebhookMetadata#shop` to look up/act on that shop's data (as the library's own docs direct: `handler.handle(data: WebhookMetadata.new(topic: ..., shop: request.shop, ...))`), this is a cross-tenant data integrity break — the receiving app can be tricked into applying attacker-supplied event data (body) under a victim shop's identity.

### Likelihood Explanation
Requires only: (1) the attacker/merchant installs the target app on any shop (no special privilege), (2) captures one legitimately Shopify-signed webhook delivery whose body is either empty or reproducible/attacker-influenced, and (3) replays it to the app's public webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, access tokens, or the app's `client_secret` is required.

### Recommendation
Bind the shop (and topic/webhook id) into the HMAC-verified material, or otherwise cryptographically tie the header-derived shop to the payload before trusting it — e.g., verify the shop domain against the caller's own registered/authenticated session/shop record rather than trusting the unsigned header, or require the host app to independently authenticate the shop before consuming `WebhookMetadata#shop`. At minimum, document prominently that `shop` in `WebhookMetadata` is not authenticated by the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers any webhook event whose body is empty or fully known (e.g., some topics deliver `{}`).
2. Shopify sends: `POST /webhooks` with headers `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid HMAC of body>`, body `{}`.
3. Attacker resends the same request to the app's webhook endpoint but swaps the header to `shopify-shop-domain: victim-shop.myshopify.com`, keeping body and HMAC identical.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks the raw body against the HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches to the handler, which now acts as though the event came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
