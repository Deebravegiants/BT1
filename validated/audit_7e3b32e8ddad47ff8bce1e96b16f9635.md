### Title
Webhook `shop` (and `topic`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then trusts the unauthenticated `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`) headers to decide which merchant/tenant the event belongs to. Because the HMAC signature never binds the `shop` value, an attacker who can obtain one valid `(body, hmac)` pair for the app (e.g., from their own shop's legitimate webhook delivery, since the webhook secret is the app's single `client_secret` shared across all merchants) can replay that same body/hmac while substituting an arbitrary `shop` header, causing the app to process the event as if it came from a different, victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

`Request#shop` and `Request#topic` are read directly from HTTP headers, which are never part of the signed material: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's handler, without any additional binding check between the signed body and the claimed shop: [4](#0-3) 

Identity binding broken: `hmac_valid(body) == true` is treated as equivalent to `shop_header == authentic_source_shop`, but the HMAC key (`Context.api_secret_key`) is the same for every shop that has installed the app. Any of the app's own installing shops can capture a legitimately-signed `(body, hmac)` pair from their own real webhook deliveries and retransmit it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a different, victim shop. The signature still validates (it only checks the body bytes against the shared secret), so `Registry.process` dispatches the event to the handler labeled as coming from the victim tenant.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: the app is designed to key persistence/business logic off `WebhookMetadata#shop`, and this value can be spoofed independently of the HMAC-verified payload. This matches the "Critical – cross-tenant access" category in the disclosure criteria, since a single unprivileged app-installer (one merchant) can cause the host application to attribute arbitrary webhook payloads/events to another merchant's tenant.

### Likelihood Explanation
The precondition is only that the attacker has installed the app on some shop of their own (a normal, unprivileged install) and can observe at least one raw webhook body + HMAC pair sent to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged credential is required — the webhook endpoint is a plain internet-reachable HTTP endpoint, and the shared secret used for the HMAC is not shop-specific.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the material that is verified, e.g., include the relevant Shopify headers in the signable string, or independently verify that the claimed `shop` corresponds to a session/shop the application actually expects for that specific webhook subscription, before dispatching to handlers.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the raw request body `B` and its `X-Shopify-Hmac-Sha256` header value `H` sent to the app's webhook endpoint.
2. Send a new HTTP POST to the same webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (valid, since it only signs `B`), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and the desired `X-Shopify-Topic`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against the shared secret; `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"`, causing the host app to process/act on data attributed to the victim tenant despite the payload actually originating from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-23)
```ruby
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
