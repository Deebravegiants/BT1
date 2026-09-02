### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks covers the payload bytes but never the `shop-domain`/`x-shopify-shop-domain` header. `Webhooks::Registry.process` accepts any request whose body HMAC validates and then forwards the header-derived `request.shop` value to the app's handler as the trusted tenant identifier, breaking the binding `HMAC-verified-bytes == identity-acted-on`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. `HmacValidator.validate_signature` computes the HMAC over exactly that signable string and compares it with `verifiable_query.hmac`: [2](#0-1) 

`Registry.process` uses this validator as the sole authentication check before handing off the request to the registered handler, and it takes `request.shop` — parsed straight from the unauthenticated header — as the tenant identity passed into `WebhookMetadata`: [3](#0-2) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed body: [4](#0-3) 

Because the signature only certifies "these bytes were HMAC'd with the app's secret," while the shop identity used by the handler comes from an unsigned header, the equality `bytes verified == identity acted on` does not hold. Any party who can obtain one valid `(raw_body, hmac)` pair for the app's secret — e.g., an unprivileged merchant who has legitimately installed the app in their own store and thus receives genuinely signed webhook deliveries for their own shop — can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value. The HMAC check still passes (it never looked at the header), and the handler receives `WebhookMetadata` claiming the event belongs to a different, victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: an app that keys per-shop actions (e.g., updating the record for `data.shop`, triggering shop-specific business logic, or writing audit/webhook logs attributed to a shop) using `WebhookMetadata#shop` can be made to attribute a payload to a shop that never sent it. This is a cross-tenant confusion primitive — the attacker controls both the body content (their own real webhook, or any topic-shaped body they can get legitimately signed) and the shop the app believes it came from, without needing the `api_secret_key` or any privileged token.

### Likelihood Explanation
Likelihood is moderate: the attacker must possess at least one valid `(body, hmac)` pair, which any unprivileged user with their own store and app installation can readily obtain simply by using the app normally (webhooks are delivered to a merchant's own endpoint configuration, and the raw request/headers can be captured and replayed with a modified shop header via any HTTP client). No secret material or privileged access is required — only the ability to send an HTTP request to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and other trust-relevant headers such as topic and api-version) as part of the signable string used for HMAC verification, or otherwise independently authenticate the shop before trusting `request.shop`/`WebhookMetadata#shop`. If per-Shopify semantics genuinely require the HMAC to cover only the body (matching platform behavior), the header value should never be treated as an authenticated tenant identifier by downstream consumers without a secondary check (e.g. confirming the shop has a known/registered session, or that the topic+shop combination matches an outstanding registration).

### Proof of Concept
1. Install the target app normally in an attacker-controlled development store, so Shopify begins sending legitimately HMAC-signed webhooks to the app's webhook endpoint.
2. Capture one such delivered webhook request in full, in particular its raw body and its `x-shopify-hmac-sha256` header value.
3. Replay this exact `(raw_body, hmac)` pair to the same webhook endpoint, changing only the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to a different, victim shop's domain.
4. `HmacValidator.validate` succeeds because it only recomputes the HMAC over `raw_body`: [5](#0-4) 
5. `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the victim's domain even though the payload actually originated from the attacker's own store: [6](#0-5)

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
