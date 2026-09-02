## Title
Webhook `shop` (and topic/version/id) fields are not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, but exposes `shop`, `topic`, `api_version`, and `webhook_id` from HTTP headers that are never included in that signature. `Registry.process` trusts these unauthenticated header values (in particular `shop`) and hands them straight to the app's webhook handler, breaking the binding: `bytes verified` (`raw_body`) ≠ `bytes acted on` (`raw_body` + `shop` header).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from headers with no cryptographic binding to the signature: [2](#0-1) 

Validation only checks the HMAC over `to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` accepts the request once the HMAC on the body passes, and then forwards the unauthenticated `request.shop` header value into the handler as the tenant identifier for the webhook payload: [4](#0-3) 

Crucially, the HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that installs the app — it is not shop-specific. This means any merchant who installs the app on their own store (an unprivileged internet user from the perspective of any other tenant) receives correctly-HMAC-signed webhook deliveries for their own shop. Because the signature covers only the body and not the `shop-domain` header, that attacker can capture one such legitimately-signed delivery and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds because the body and secret are unchanged, so `Registry.process` will invoke the app's handler with `shop: <victim shop>` and the attacker-chosen body content.

### Impact Explanation
This breaks the identity binding `shop authenticated == shop the app acts on`, letting a low-privilege actor (any merchant able to install the app) inject data/events attributed to an arbitrary other tenant (shop domain) into the host application, since the gem itself performs no cross-check between the authenticated payload and the claimed shop. Any application logic that uses `WebhookMetadata#shop` to select which tenant's records to update, create, or delete is exposed to cross-tenant data corruption/injection — this falls under the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any app author who installs on their own store (a normal, unprivileged flow — no leaked secrets, no privileged Shopify access needed): they legitimately receive one correctly signed webhook, then only need to modify a plain HTTP header before replaying it to the public webhook endpoint.

### Recommendation
Include the header-derived values (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the signed payload, so that a valid signature can only be produced/replayed for the exact shop/topic/version combination it was generated for.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook POST: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Replay the exact same request to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (leave `B` and `H` untouched).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H})` is constructed.
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only and it matches `H` → validation passes.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed B, ...)`, letting the attacker inject data attributed to `victim.myshopify.com`. [5](#0-4) [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
