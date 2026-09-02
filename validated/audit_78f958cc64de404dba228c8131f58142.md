## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant spoofing of processed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `api_version`, `webhook_id`) values from unsigned HTTP headers, while the HMAC signature that `Registry.process` validates only covers the raw request body. An unprivileged actor who legitimately receives one signed webhook (e.g., by installing the app on their own store) can replay that exact body with a forged `x-shopify-shop-domain` header pointing at a different shop, and the signature will still validate.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC over `verifiable_query.to_signable_string`, and for webhooks that string is only the raw JSON body: [1](#0-0) [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from headers that are never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) directly to dispatch to the handler, without any additional binding between the signed body and the shop/topic claimed by the headers: [3](#0-2) 

The identity binding that should hold is: `shop header == shop that the HMAC-signed body was generated for`. Because the HMAC only covers `@raw_body`, that equality is never checked — `hmac_is_valid(body) ⇏ shop_header == originating_shop`. An attacker who receives a legitimately-signed webhook body for their own shop (trivial: install the app on a store they control, or replay any webhook delivery they can observe/capture) can resend it to the app's webhook endpoint with the `shop-domain` (and even `topic`/`webhook-id`) header replaced with an arbitrary victim shop identifier. The signature check in `HmacValidator.validate_signature` still passes because it only recomputes HMAC over the untouched body: [4](#0-3) 

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (built directly from `request.shop`) to key merchant data — e.g., to look up a session/store record, attribute the payload to a tenant, or write into per-shop storage — an attacker can cause data belonging to their own store to be attributed to, or processed under, an arbitrary victim shop domain, or vice versa. This is a cross-tenant data/identity confusion vulnerability rooted entirely in this gem's webhook verification logic, matching the Critical "cross-tenant access" impact category, since the gem is what is relied upon to assert "this data really came from shop X."

### Likelihood Explanation
Any unprivileged user who can install the target app on a shop they control (or who can intercept/replay a single valid webhook delivery) can mount this attack with a simple HTTP replay — no access token, `client_secret`, or privileged account is required, only knowledge of the app's public webhook endpoint and one previously-observed valid webhook body/HMAC pair for any shop.

### Recommendation
Include the shop domain (and other headers acted upon, such as topic/webhook-id) in the signable payload that is HMAC-verified, or otherwise independently bind `request.shop` to the specific delivery (e.g., verify it against a value embedded in the signed body, or require the host app to cross-check `shop` against an authenticated session/installation record before trusting it). At minimum, `Utils::VerifiableQuery#to_signable_string` for webhooks should be changed to incorporate the `shop-domain` header value so that tampering with it invalidates the signature.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com`, triggers a webhook (e.g., `orders/create`) and captures the raw POST body and the valid `x-shopify-hmac-sha256` header Shopify sent for it.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` — it matches because the body wasn't altered: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata` whose `shop` is `"victim.myshopify.com"` even though the payload never touched Shopify's systems for that shop: [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
