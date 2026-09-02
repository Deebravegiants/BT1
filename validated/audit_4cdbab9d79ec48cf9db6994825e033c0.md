### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the body, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, and never binds the `x-shopify-shop-domain` (or `shopify-shop-domain`) header into that signature. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and, on success, unconditionally trusts `request.shop` (parsed straight from the header) to build the `WebhookMetadata` handed to the app's `WebhookHandler`. Because the tenant identity (`shop`) is not covered by the same authentication check as the payload, an attacker who can obtain any one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` can replay it with a forged `shop` header and have the gem present it to the host app as an authentic webhook for an arbitrary victim shop.

### Finding Description
`Utils::VerifiableQuery`/`HmacValidator` compute the HMAC over whatever `to_signable_string` returns. For webhooks, that is only the raw body: [1](#0-0) [2](#0-1) 

The `shop` accessor is read directly from an attacker-controllable HTTP header, with no cryptographic binding to the signed body: [3](#0-2) 

`HmacValidator.validate` recomputes the HMAC solely from `to_signable_string` (the body) and compares it to the `hmac` header — it has no notion of `shop` at all: [4](#0-3) 

`Registry.process` performs exactly this check and then forwards `request.shop` — unauthenticated, unbound to the signature — straight into the struct that is handed to the host application's handler: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `hmac == HMAC(secret, body ∧ shop)`. What the gem actually verifies is `hmac == HMAC(secret, body)`, with `shop` never entering the signed material. Because Shopify webhook HMACs are signed with a single `api_secret_key` per app (not per shop/tenant), any `(body, hmac)` pair the attacker legitimately received for one installed shop remains cryptographically valid for every other shop the same app serves. Swapping the `shop` header on replay therefore passes `HmacValidator.validate` unchanged while completely changing the tenant that `WebhookMetadata#shop` reports to the handler.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: a party with access to one authentic webhook body+HMAC pair for shop A (e.g., because they operate a store that has the app installed, or because a webhook payload/HMAC pair leaked/was observed) can replay it against the app's webhook endpoint declaring `x-shopify-shop-domain: shop-b.myshopify.com`. The gem will accept it as authentic (HMAC validates) and pass `shop: "shop-b.myshopify.com"` to the host handler. Any host logic that keys data lookups, GDPR redaction, order/customer updates, or access-token retrieval off `WebhookMetadata#shop` can be tricked into acting on/against the wrong merchant's tenant data — a cross-tenant confusion rooted entirely in this gem's verification logic, not merely a documentation gap the host app failed to follow.

### Likelihood Explanation
Exploitation requires only one legitimately-received webhook (body + valid `hmac-sha256` header) from any shop where the attacker's app is installed (trivially obtainable by the attacker in their own test/demo store) plus the ability to POST to the app's public webhook endpoint with a modified `shop` header — no access token, secret, or privileged account is needed. This is a low-effort, unprivileged-internet-user attack path.

### Recommendation
Bind the shop identity into the authenticated material before trusting it: include `shop-domain` (and ideally `webhook-id`/`api-version`) in `to_signable_string`, or independently verify that `request.shop` matches an expected/registered shop domain (e.g., an active session for that shop) before dispatching to the handler, rather than trusting the raw header once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets it trigger any webhook topic (e.g. `orders/create`), capturing the raw request body `B` and the `x-shopify-hmac-sha256` header value `H` sent by Shopify.
2. Attacker sends a forged POST to the app's webhook endpoint with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: H` (unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - body: `B` (unchanged)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds.
4. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` and invokes the host's handler, which now believes this authentic-looking event belongs to `victim-shop.myshopify.com` even though it was never sent by Shopify for that shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
