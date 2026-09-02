## Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the shop identity (`shop-domain` header) and other metadata handed to the app's handler are taken verbatim from unauthenticated HTTP headers. Because the HMAC never binds those headers, a merchant who legitimately receives one valid `(body, hmac)` pair for their own shop can replay it to the same webhook endpoint with a forged `shop-domain` header, causing the host application to process attacker-controlled data as if it originated from a different, victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers with no cryptographic tie to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string`, i.e. it only recomputes and compares the HMAC of the raw body against the secret; it never inspects or binds the headers: [3](#0-2) 

`Registry.process` uses this single HMAC check as the sole authentication gate, then forwards the unauthenticated header-derived `request.shop` (along with `topic`, `webhook_id`, `api_version`) straight to the application handler as trusted identity metadata: [4](#0-3) 

The identity binding that should hold is:
`authenticated(shop-domain header) == shop that produced the HMAC-signed body`

In reality the check only proves:
`HMAC(raw_body, api_secret_key) == received_hmac`

which says nothing about which shop the body came from, since the `api_secret_key` is shared by the app across **all** shops that install it (a multi-tenant secret), and no field in `raw_body` is required to match the `shop-domain` header. Any shop that can legitimately trigger one webhook for itself (e.g., updating one of its own orders/products) obtains a valid `(raw_body, hmac)` pair signed with the app's real secret. That shop can then send a forged HTTP request directly to the app's public webhook endpoint, keeping `raw_body`/`hmac` unchanged but substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header values to point at a different, victim shop. `HmacValidator.validate` still returns `true` because it never looked at those headers, and `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
Any host application that relies on `WebhookMetadata#shop` (as documented and demonstrated in `docs/usage/webhooks.md`) to resolve which merchant/tenant a webhook event applies to — e.g., to look up that shop's session, update that shop's local records, or trigger per-shop side effects — can be made to attribute attacker-supplied body content to an arbitrary victim shop known only by its `.myshopify.com` domain. This is a cross-tenant integrity/identity-binding failure: data ostensibly "from shop A" can be delivered and processed as "from shop B" without possessing shop B's credentials, satisfying the "cross-tenant access" impact bar.

### Likelihood Explanation
The attacker only needs to be a legitimate (even free-trial) merchant with the target app installed on their own store — they do not need the app's `client_secret`, an access token, or any privileged account. They can trivially trigger a webhook for their own shop (e.g., edit a product), capture the resulting `raw_body` + `X-Shopify-Hmac-Sha256`, and POST it directly to the app's public webhook URL with modified `shop-domain`/`topic`/`webhook-id` headers using any HTTP client. No timing race or secret material is required, only network access to the app's webhook endpoint, making this straightforward to execute for any unprivileged internet user who is also a merchant of the app.

### Recommendation
Bind the shop/topic/webhook-id metadata to the authenticated payload instead of trusting raw headers:
- Include `shop-domain`, `topic`, and `webhook-id` in the signable string used for HMAC verification (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes all relevant fields, not just one), or
- Cross-check the header-derived `shop` against an independently verified source (e.g., the shop stored for the session that registered the webhook) before dispatching to the handler, rejecting mismatches.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers/receives a webhook (e.g., `products/update`) for it, capturing the raw POST body `B` and the header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(B, api_secret_key)`.
2. Attacker sends a new HTTP POST directly to the app's public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers, `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(B, api_secret_key) == H`: [5](#0-4) 
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: JSON.parse(B), ...)`: [6](#0-5) 
5. The host application processes attacker-controlled body content believing it came from `victim.myshopify.com`.

### Citations

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
