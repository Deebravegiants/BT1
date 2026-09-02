## Title
Webhook `shop-domain` and `topic` headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the webhook request body via HMAC, but the `shop`, `topic`, `webhook_id`, and `api_version` values that the library hands to the handler as trusted "who sent this" metadata come from unauthenticated HTTP headers that are never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authenticating the entire request, then forwards the *unauthenticated* `shop` and `topic` header values to the app's handler as trusted identity fields: [4](#0-3) 

This breaks the identity binding `shop header == shop that produced the signed bytes`. The HMAC only proves "this body byte sequence was signed with the app's shared client secret at some point," not "this body came from shop X." Because the same `api_secret_key`/client secret is shared across *every* shop that installs the app, any merchant with a legitimate install (an unprivileged, low-trust actor from the app's perspective) can capture one authentic webhook delivery (valid body + valid HMAC), then replay it to the app's webhook endpoint with the `shop-domain` (and/or `topic`/`webhook_id`) header rewritten to a victim shop. The HMAC check still passes because the signature never covered those headers, and `Registry.process` hands the forged `shop` straight to `WebhookMetadata`/the handler as the authenticated tenant identifier.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (as returned by this library) to attribute the event to a tenant — e.g., to look up a merchant record, write order/inventory data, or trigger merchant-specific side effects — an attacker who only controls their own (unprivileged) shop installation can inject fabricated webhook events attributed to an arbitrary victim shop. That is cross-tenant data injection/spoofing: the equality `shop asserted in header == shop that cryptographically produced the request` fails to hold, yet the library treats the check as sufficient proof of origin for that shop.

### Likelihood Explanation
Exploitation only requires the attacker to have (or create) one legitimate, low-privilege app installation — a webhook subscription on any shop running the app is enough to obtain a valid `(body, hmac)` pair, since the signing secret is shared across all installs. No access to `api_secret_key`, tokens, or the target shop is needed; the attacker only edits headers on their own outbound HTTP request to the app's public webhook endpoint.

### Recommendation
Do not treat headers outside the signed payload as authenticated. Either:
- Include `shop-domain`, `topic`, and `webhook_id` in the signable string used for HMAC computation, or
- Require the consuming application to cross-check `request.shop` against an already-known, previously-authenticated session/shop record (e.g., a stored session for that shop) before trusting the webhook as belonging to that tenant, and document this requirement clearly since the library currently implies HMAC validation is sufficient identity proof.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and receives a legitimate webhook delivery:
   - `x-shopify-hmac-sha256: <valid HMAC of body B>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - body: `B`
2. Attacker resends the exact same body `B` and HMAC header to the app's webhook endpoint, but changes:
   - `x-shopify-shop-domain: victim.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only `B` (unchanged) was signed: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and the host app processes/attributes the (attacker-controlled) body as an authentic event from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
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
