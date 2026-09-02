### Title
Webhook shop-domain identity is trusted without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The Cosmos SDK advisory describes a case where an unauthenticated/unvalidated piece of proposal data was acted upon without being properly bound to the check that was supposed to gate it, leading to an inconsistent state. The analogous class of bug in this gem is a field that is *acted upon* by the library but *not covered* by the cryptographic integrity check (HMAC) that is supposed to authenticate the whole message. In `ShopifyAPI::Webhooks::Request`, the `shop` (tenant identity) is read straight from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature only covers the raw request body, never the shop header.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

The `shop` domain is pulled from an HTTP header that is not part of that signed string: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC of the request (which only covers `@raw_body`), and then forwards `request.shop`—the unauthenticated header—directly to the app's handler as the tenant identifier, with no re-validation against the signed content: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field consumed by any host application's `WebhookHandler#handle` implementation to decide which merchant/tenant the payload belongs to: [4](#0-3) 

The identity binding that is broken is:
`hmac_valid(raw_body, secret) == true` is treated as `shop_header == authenticated_shop_of(raw_body)`,
but in reality `hmac_valid(raw_body, secret)` only proves the *body* bytes are authentic; it says nothing about which shop the header claims to be. `HmacValidator.validate` confirms only that the signature matches the signable string (the body), not that the shop header is bound to the signature: [5](#0-4) 

### Impact Explanation
Any party who legitimately receives a validly-HMAC-signed webhook body for their own store (e.g., an attacker who installs the app on their own Shopify shop and thus receives real webhooks with valid HMACs) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different value in the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header. Because the header is not part of the signed payload, `Utils::HmacValidator.validate` still returns true, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to a victim shop. If the host application uses `data.shop` to select which tenant's session/access token/database row to act on (the documented and expected usage pattern for this struct), this results in cross-tenant data confusion — data intended for/about the attacker's shop gets attributed to and processed under a different merchant's identity. This matches the "cross-tenant access" Critical-impact category defined in scope.

### Likelihood Explanation
This requires only an internet-reachable webhook endpoint and possession of at least one genuinely-signed webhook (obtainable trivially by installing the app on a shop the attacker controls, which any unprivileged user can do for public apps). No access token, `client_secret`, or privileged account is required — only a header rewrite on replay, which is well within reach of an unprivileged actor and does not depend on the host app "ignoring documented API"; the shop field is presented by this gem's `WebhookMetadata` as if it were an authenticated identity field, which it is not.

### Recommendation
Include the shop domain (and ideally topic, api-version, webhook-id) in the HMAC-signed material, or independently verify `request.shop` against a known/expected list of installed shop domains before dispatching to handlers, so `WebhookMetadata.shop` cannot be set independently of the signature that authenticates the payload.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and captures a legitimate webhook POST, e.g. `orders/create`, with header `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Utils::HmacValidator.validate` succeeds because it only checks the body against the HMAC: [3](#0-2) 
4. The app's `WebhookHandler#handle` receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled order body, and processes it as if it were genuine data belonging to `victim-shop`.

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
