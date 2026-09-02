### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity used by webhook handlers from the unauthenticated `x-shopify-shop-domain` HTTP header, while the HMAC signature (`Utils::HmacValidator.validate`) only covers the raw request body. This breaks the binding `HMAC-verified bytes == data acted upon`, allowing a party who legitimately receives real, validly-signed webhooks for one shop (e.g., because they installed the target public app on their own store) to replay the exact same signed body against the app's webhook endpoint with a forged `shop-domain` header pointing at a victim shop.

### Finding Description
`Request#hmac` reads the signature from the `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`shop` is read independently from the `shop-domain` header and is never part of the signed content: [3](#0-2) 

`Registry.process` validates the HMAC over the body only, then hands `request.shop` straight to the handler as the trusted tenant identifier, with no separate check that the shop is the one the webhook subscription belongs to: [4](#0-3) 

`HmacValidator.validate_signature` uses `verifiable_query.to_signable_string` (the raw body for webhooks) as the signed material and `OpenSSL.secure_compare` against the header HMAC — correct comparison, but it verifies bytes that don't include the shop domain, topic, webhook id, or api version: [5](#0-4) 

The binding that should hold is:
`hmac_valid(raw_body) ⇒ shop-domain header is authentic`

but the actual binding is only:
`hmac_valid(raw_body) ⇒ raw_body is authentic (signed by the app's own client_secret at some point, for some shop)`

Because Shopify signs webhooks per-app (using the app's `client_secret`), not per-shop, any shop that has the target app installed receives webhooks signed with the *same* secret. An attacker who installs a public app on their own store obtains genuine webhook deliveries with valid HMACs. They can then capture such a delivery and replay the identical raw body to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (as returned by this gem) to key per-tenant storage or trigger tenant-scoped actions (a usage pattern the gem itself encourages via `WebhookMetadata.new(... shop: request.shop ...)`), an attacker can inject data attributed to, or trigger side effects against, a shop they do not control — a cross-tenant access/integrity issue. This satisfies the Critical bucket ("cross-tenant access") since the attacker never needs the target's or the app's secret; they only need their own legitimate installation of the same public app plus the ability to POST to the app's webhook URL.

### Likelihood Explanation
Medium-to-high: exploitation only requires installing a public app (something any unprivileged internet user with a Shopify dev/trial store can do), capturing one real webhook delivery to learn a valid `(body, hmac)` pair, and replaying it with a modified `shop-domain` header to the app's webhook receiver endpoint (which is a public URL by design). No credentials, access tokens, or the app's `client_secret` are required by the attacker.

### Recommendation
Bind the shop domain (and other trust-relevant metadata such as topic/webhook id) into the signed material, or independently verify that the `shop-domain` header corresponds to a shop that actually has the corresponding webhook subscription/topic registered (e.g., cross-check against Shopify via the GraphQL Admin API, or maintain a mapping of installed shops) before trusting `WebhookMetadata#shop`. At minimum, document prominently that `shop` from `WebhookMetadata` must not be treated as authenticated by the HMAC and must be independently corroborated by the host application.

### Proof of Concept
1. Attacker installs the target public Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) and captures the delivered request: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker POSTs to the app's public webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)` and compares to `H` via `OpenSSL.secure_compare` — it matches because the shop domain was never part of the signed input. [5](#0-4) 
5. `Registry.process` invokes the registered handler with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the payload actually originated from the attacker's own shop. [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
