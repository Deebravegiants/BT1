### Title
Webhook shop-domain identity is not bound to the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely via `Utils::HmacValidator.validate(request)`, but the HMAC only covers the raw JSON body, not the `shop-domain` header that the gem then trusts as the tenant identity passed to the handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
`HmacValidator.validate_signature` computes and compares the HMAC over exactly that signable string: [2](#0-1) 
`Registry.process` checks only this HMAC and then forwards `request.shop` (the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) straight to the app's handler as the tenant identity: [3](#0-2) 
`Request#shop` is read directly from headers with no cross-check against the HMAC-signed content: [4](#0-3) 

The identity binding broken is: `shop authenticated (bytes covered by HMAC)` ≠ `shop delivered to the handler as the tenant key (shop-domain header, unauthenticated)`. Because the shop domain is not part of `to_signable_string`, any request whose body+HMAC pair is valid for the shared `api_secret_key` will be accepted for **any** shop-domain header value, regardless of which shop's webhook actually produced that HMAC.

### Impact Explanation
An unprivileged user who is a legitimate merchant/tenant of a multi-tenant app (i.e., has installed the app on their own store, generating real webhooks signed with the app's shared `api_secret_key`) can capture one of their own valid `(body, HMAC)` pairs and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. The gem will pass this HMAC-verification and hand the handler a `WebhookMetadata` claiming the payload originated from the victim's shop with attacker-controlled `body`/`topic`. Any host application that uses `data.shop` from the gem's `WebhookMetadata` to select a per-tenant session, database row, or webhook queue (the documented usage pattern) will process attacker-controlled data as if it belongs to another tenant — a cross-tenant data-integrity/confusion issue that can escalate to cross-tenant access if the handler uses `shop` to fetch/act on that tenant's stored access token or state.

### Likelihood Explanation
Moderate-to-high: exploitation requires no secret knowledge beyond what a normal installed merchant already legitimately possesses (their own valid webhook deliveries), and no privileged access to the app or Shopify's infrastructure — only the ability to replay an HTTP request with a modified header, which satisfies the "unprivileged internet user" bar. The main constraint is that the attacker must control (or tolerate) the body content of their own real webhook, which is often sufficient (e.g., `orders/create`, `customers/create`/`app/uninstalled` bodies contain attacker-influenced fields such as shop-owned resource IDs, notes, or metafields).

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or independently verify that `request.shop` corresponds to a shop with an active, previously-established session/installation before dispatching to the handler, so the identity used by the handler is cryptographically bound to the same bytes that were verified.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, receiving legitimately signed webhooks (e.g. `orders/create`) with header `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`.
2. Attacker replays the exact same raw body and HMAC to the app's webhook endpoint, but changes the header to `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(body, secret)` [5](#0-4) .
4. `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker-controlled>, ...)` [6](#0-5) , causing the host app to process attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
