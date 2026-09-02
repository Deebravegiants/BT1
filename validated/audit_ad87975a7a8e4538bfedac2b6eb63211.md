### Title
Webhook shop/topic identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw HTTP body via HMAC, but the `shop` (and `topic`) fields that the rest of the library and any registered handler treat as trusted, tenant-identifying data are taken from unauthenticated HTTP headers that are never included in the signed payload. Anyone who can obtain one valid `(raw_body, hmac)` pair for the app (trivially available to any merchant who installs the app on their own store) can replay that exact body/HMAC pair while swapping the `shop-domain` header to a victim shop, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic.

### Finding Description
`Webhooks::Request#to_signable_string` only returns the raw body: [1](#0-0) 

while `shop` and `topic` are pulled straight from attacker-controllable headers with no cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC exclusively over `to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header value — it never incorporates `shop` or `topic`: [3](#0-2) 

`Webhooks::Registry.process` uses this HMAC check as its sole authenticity gate, then forwards the unauthenticated `request.shop` value straight into `WebhookMetadata`, which application handlers use to identify which tenant the event belongs to: [4](#0-3) 

The identity binding that should hold is:
`bytes_verified_by_HMAC == bytes_that_determine_the_tenant("shop")`

but here `bytes_verified_by_HMAC = raw_body` while `bytes_that_determine_tenant = shop-domain header`, so the two are disjoint. Any attacker who is a legitimate (but unprivileged, non-victim) installer of the app on their own store receives real Shopify-signed webhooks for their own shop — a completely valid `(raw_body, hmac)` pair signed with the app's secret. Because `shop-domain` isn't part of the signed content, that exact pair can be replayed against the app's webhook endpoint with the `shop-domain` header rewritten to any other shop the attacker does not control, and the HMAC check in `HmacValidator.validate` still passes.

### Impact Explanation
This breaks the tenant-authentication guarantee the gem is documented to provide via `Webhooks::Registry.process`/`WebhookMetadata#shop`: an unprivileged attacker (any merchant who can install the app) can spoof webhook events as originating from a shop they do not control. Any app handler that uses `data.shop` to look up per-tenant sessions, trigger tenant-scoped side effects, or make cross-tenant trust decisions (e.g. `app/uninstalled`, `shop/update`, GDPR events, or custom business events) can be fed forged tenant identity, constituting cross-tenant access/confusion — a Critical-class impact per the given severity rubric.

### Likelihood Explanation
Likelihood is Low/Moderate: it requires (1) installing the app on an attacker-controlled shop to obtain a valid signed `(body, hmac)` pair — a normal, unprivileged action — and (2) sending a forged HTTP request to the app's public webhook endpoint with a rewritten `shop-domain` header, which is straightforward since headers are not signed. No access to `api_secret_key`, tokens, or victim credentials is required.

### Recommendation
Include `shop` and `topic` (and ideally `webhook_id`/`api_version`) in the HMAC-signed payload validation, or otherwise cryptographically bind these header-derived identity fields to the request body before trusting them (e.g., verify HMAC over a canonical string containing body + shop + topic, matching how Shopify's own webhook signing scheme is documented, or require the app to independently confirm `shop` against a known/installed-shops list before acting on the event).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal unprivileged installation).
2. Shopify sends a legitimate webhook to the app: body `B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)`.
4. Attacker sends their own POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — matches `H`, so validation succeeds: [5](#0-4) 
6. The handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` even though the event body/content actually originated from the attacker's own shop, achieving tenant spoofing.

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
