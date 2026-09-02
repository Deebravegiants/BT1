Confirms the asymmetry: `AuthQuery#to_signable_string` binds `shop`, `code`, `state`, `host`, `timestamp` into the signed string, but `Webhooks::Request#to_signable_string` only returns `@raw_body`, leaving `shop`, `topic`, and `webhook_id` headers completely outside the HMAC's coverage. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop identity not bound by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature verified by `Utils::HmacValidator` covers the JSON payload but not the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers. `Registry.process` trusts `request.shop` for dispatch to the app's handler without that value ever being covered by the signature.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received HMAC. [4](#0-3) 
For `Webhooks::Request`, `to_signable_string` is simply `@raw_body`: [1](#0-0) 
Meanwhile `shop`, `topic`, and `webhook_id` are all read straight from unauthenticated headers: [5](#0-4) 
`Registry.process` validates only the HMAC over the body, then immediately dispatches to the app's handler using the unauthenticated `request.shop`/`request.topic`/`request.webhook_id`: [3](#0-2) 

The equality the code implicitly assumes is: *`shop` used by the app handler == `shop` that Shopify actually signed for*. In reality, the HMAC only proves *`raw_body` was signed by Shopify's `client_secret`*; it says nothing about which shop, topic, or webhook id that body was signed for. This is the same class of bug as the reported "bytes verified versus bytes parsed" pattern: the code verifies one set of bytes (the body) but acts on a different, unverified set of bytes (the headers) as if they carried the same trust guarantee.

By contrast, the OAuth callback's `AuthQuery#to_signable_string` correctly binds `shop` into the signed string so that `shop` cannot be swapped post-signature: [6](#0-5) 
No equivalent binding exists for webhook headers.

### Impact Explanation
Any low-privileged actor who has legitimately received one authentic webhook delivery for a shop they control (e.g., they install any Shopify app tied to the same `client_secret`/app, or simply capture their own store's webhook payload) can replay that exact `raw_body` + valid `hmac-sha256` value to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for any victim shop domain, and/or the `X-Shopify-Topic`/`X-Shopify-Webhook-Id` headers. Because `Registry.process` only checks the body's HMAC and forwards `request.shop`/`request.topic` unchanged to `WebhookMetadata`, the app's handler will process attacker-controlled data attributed to a victim tenant — a cross-tenant data injection/spoofing primitive (e.g., faking `orders/create`, `app/uninstalled`, or `customers/data_request` events for a shop the attacker does not own). This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires no secrets beyond a single legitimate webhook capture (achievable by any merchant who installs the app on their own store) and simple HTTP header manipulation when replaying to the app's public webhook endpoint. No `api_secret_key`, access token, or privileged account is required.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the HMAC-verified surface. Since Shopify itself doesn't sign headers, the safest fix is for `Registry.process`/handlers to independently authenticate `request.shop` against the shop associated with the topic's known/expected registration (e.g., a stored per-shop webhook secret or an allow-list of installed shops) rather than trusting the header value alone. At minimum, document and enforce that consuming apps must cross-check `request.shop` against their own installed-shop records before acting on webhook data, since the gem cannot itself verify header-shop authenticity via HMAC.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body and the valid `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker POSTs the identical body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` succeeds because it only re-hashes `@raw_body`, which is unchanged. [7](#0-6) 
4. `Registry.process` calls `handler.handle` with `shop: request.shop` set to `victim-shop.myshopify.com`, even though Shopify never signed that shop domain for this body, letting the app process attacker data as if it originated from the victim tenant. [8](#0-7)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
