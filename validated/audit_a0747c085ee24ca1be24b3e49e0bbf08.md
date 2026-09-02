Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and the HMAC binds nothing else.### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) attribution is not covered by the HMAC signature, allowing tenant misattribution of a validly-signed webhook payload - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `Utils::HmacValidator.validate` only authenticates the JSON body bytes. The `shop`, `topic`, `api_version`, and `webhook_id` fields are read straight from HTTP headers and are never included in the signed content, yet `Registry.process` uses `request.shop` (and `topic`) — unauthenticated header data — to select the handler and to build the `WebhookMetadata` that is handed to the app's `handle` callback as the identity of the tenant that produced the event.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac` [1](#0-0) . For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled from HTTP headers with no cryptographic binding to the HMAC: [3](#0-2) 

`Registry.process` trusts `request.shop` as the tenant identity when dispatching to the handler: [4](#0-3) 

This breaks the intended identity binding: `HMAC(secret, body) == received_hmac` is treated as proof that `(body, shop)` originated from Shopify for that `shop`, when in reality the equality only proves `body` is authentic — `shop` is attacker-supplied and unverified. Because `Context.api_secret_key` (the client secret) is a single, global-per-app value shared across every shop that has the app installed [5](#0-4) , any party who has the app installed on a shop they control receives correctly-HMAC-signed webhook deliveries for that shop. They can capture one `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header claiming a different (victim) shop, and `Registry.process` will accept it as valid and dispatch `WebhookMetadata.new(shop: <attacker-chosen shop>, ...)` to the host app's handler.

### Impact Explanation
Multi-tenant apps built on this gem use `WebhookMetadata#shop` as the authoritative tenant identifier to route/attribute incoming webhook data (e.g., to decide which merchant's records to create/update/delete, or which stored `Session`/access token to use for follow-up API calls). Since this field is not bound by the HMAC, an attacker who legitimately installs the app on any shop they control can forge the tenant attribution of an otherwise-valid webhook delivery, achieving cross-tenant data injection into another merchant's records within the host application — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker install the vulnerable app on a shop they control (a normal, unprivileged action available to any Shopify merchant/developer) and be able to send an HTTP POST to the app's public webhook endpoint with modified headers, which is standard webhook-endpoint exposure. No access to `api_secret_key`, an access token, or a privileged account on the victim shop is required. The only constraint is finding/crafting a body whose data is meaningful to the target shop context, which is app-specific but does not change the fundamental signature-verification bypass.

### Recommendation
Bind the tenant-identifying and dispatch-relevant fields (`shop-domain`, `topic`, `api-version`, `webhook-id`) into the signable content used for HMAC verification, or independently verify that the `shop` header matches an expected/known tenant (e.g., cross-check against the session store) before trusting it for routing. At minimum, document/require host applications to treat `WebhookMetadata#shop` as attacker-controlled unless independently corroborated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal app installation flow) and registers/receives a real webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker sends a POST to the app's webhook endpoint with the same body `B`, the same valid `x-shopify-hmac-sha256`, but headers rewritten as:
   ```
   x-shopify-topic: orders/create
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-hmac-sha256: <same valid HMAC as step 1>
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — this passes because `B` is unmodified [6](#0-5) .
4. The app's registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` and processes/persists data as though it belongs to `victim-shop`, even though the shop header was never authenticated [7](#0-6) .

### Citations

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
