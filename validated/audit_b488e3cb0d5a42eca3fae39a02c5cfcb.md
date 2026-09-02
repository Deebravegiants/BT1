### Title
Webhook shop/topic identity spoofing due to HMAC only covering the request body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` fields — which are read directly from HTTP headers and handed to the application's webhook handler as the tenant/event identity — are never included in the signed material. This breaks the intended binding `HMAC-verified bytes == bytes the handler trusts as this shop's event`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers with no cryptographic tie to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop`/`request.topic` as the tenant/event identity passed to the host application's handler: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the raw body) against the HMAC header, so it never binds `shop`/`topic` to the signature: [4](#0-3) 

Because the app's webhook HMAC key (`Context.api_secret_key`) is the same `client_secret` for every shop that has installed the app, any store that installs the app receives genuinely-signed webhook deliveries. Since `shop-domain` and `topic` headers sit outside the HMAC, an attacker who operates their own (attacker-controlled) shop installation of the victim's app can capture a validly-signed webhook body and replay it to the same endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header naming a different, victim shop. `Registry.process` will accept it as authentic (the body HMAC still matches) and dispatch it to the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an entity authenticated only as "some shop with a valid webhook body" is treated by the handler as "shop X" of the attacker's choosing. Any host application that uses `WebhookMetadata#shop`/`#topic` to select per-tenant records (e.g., writing shop-scoped data, triggering shop-scoped side effects, or fulfilling GDPR `shop/redact`/`customers/redact` mandatory topics) can be made to act on/for a different tenant than actually sent the payload — satisfying the Critical "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on any store they control (a normal, unprivileged action for public/dev-store apps) and be able to send arbitrary HTTP requests to the app's public webhook endpoint — no leaked secrets, TLS interception, or privileged account is needed. The gem provides no header-binding, so every consumer of this library inherits the gap.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material (e.g., concatenate them with the raw body before computing/verifying the signature), or otherwise cryptographically bind these header values to the body so `HmacValidator.validate` fails if any of them are altered relative to what Shopify actually sent.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery, e.g. body `{"id":1}` with headers `X-Shopify-Hmac-Sha256: <valid hmac of body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: customers/create`.
2. Attacker resends the identical body/HMAC to the app's webhook endpoint but replaces the header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) succeeds because it only checks the unchanged raw body.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches it to the handler, which now performs shop-scoped actions attributed to the victim shop using attacker-supplied data.

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
