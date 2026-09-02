### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating the HMAC over the raw request body only, then hands the handler a `shop` value that is read from an unauthenticated HTTP header. Because the signed bytes (`raw_body`) and the trusted identity field (`shop`) are not bound together, any holder of one valid `(body, hmac)` pair — obtainable by installing the app on any shop and receiving a legitimate webhook — can replay that pair with a forged `shopify-shop-domain` header to make the app process the payload under a different tenant's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is derived purely from an HTTP header that is never included in the signed content: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, immediately trusts `request.shop` (along with `request.topic`, `request.api_version`, `request.webhook_id` — also header-derived and unsigned) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The verification uses `Utils::HmacValidator.validate`, which computes `HMAC(secret, to_signable_string)` and compares it to the received `hmac`: [4](#0-3) 

Since `to_signable_string` is just the raw body, the equality the gem actually proves is:
`HMAC(secret, raw_body) == received_hmac`

But the equality the handler relies on for tenant isolation is:
`shop_header == shop_that_produced(raw_body)`

These two are never linked. Any body/hmac pair that is valid for the app's shared `client_secret` (Shopify signs all webhooks for an app with the same secret regardless of which shop triggered them) will pass `HmacValidator.validate` no matter what `shopify-shop-domain` header accompanies it. This is the same class of defect described in the reference report: a check (`verifyLSTPriceGap`) that answers permissively because it evaluates the wrong quantity — here, the gem verifies "was this body signed by our secret?" while the handler acts on "which shop is this payload for?", and the two questions are never tied together.

### Impact Explanation
Any user who can install the target app on their own (or any) Shopify store receives legitimately-signed webhooks (signed with the app's single, per-app `client_secret`, not a per-shop secret). By capturing one such `(raw_body, hmac)` pair and resending it to the app's webhook endpoint with an arbitrary `shopify-shop-domain` (or `x-shopify-shop-domain`) header, the attacker can make the app process that payload as if it originated from a different shop. Any handler logic that uses `WebhookMetadata#shop` to key data writes/deletes, trigger per-tenant side effects, or make authorization decisions (e.g., `shop/redact`, `customers/redact`, `customers/data_request`, or ordinary data-sync handlers that store `data.shop` as the tenant key) can be tricked into acting against a victim shop's tenant data using attacker-controlled body content signed under the attacker's own installation. This is a cross-tenant identity confusion vulnerability.

### Likelihood Explanation
Exploitation requires no privileged credentials, tokens, or `api_secret_key` knowledge — only the ability to install the app once (a legitimate, unprivileged action available to any Shopify merchant/user) to obtain a valid `(body, hmac)` sample, and the ability to send arbitrary HTTP requests to the app's public webhook endpoint. The gem provides no mechanism to bind `shop` to the signed bytes, so any host application that (reasonably) trusts `WebhookMetadata#shop` as returned by this gem is exposed. This is a design gap in the gem's own webhook verification API, not merely host misuse of a documented safeguard.

### Recommendation
Include the shop domain (and other identity-bearing headers such as topic/api-version/webhook-id, where relevant) in the signed material verified against the HMAC, or independently verify that the `shopify-shop-domain` header corresponds to an active, known session/shop already established via OAuth for this app before trusting it in `WebhookMetadata`. At minimum, document and enforce that `WebhookMetadata#shop` must never be treated as authenticated by `HmacValidator.validate`, and provide a combined verification path that binds header identity fields into the signature check performed by `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, authorizing at least one webhook topic (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid HMAC over raw_body>`, and some `raw_body`.
3. Attacker captures this `(raw_body, hmac)` pair.
4. Attacker crafts a new HTTP POST to the same webhook endpoint, keeping `raw_body` and `hmac` identical, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — unchanged — and succeeds, per: [3](#0-2) 
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled `body`, believing it is a genuine event for `victim-shop`, even though no such event ever occurred at Shopify for that shop.

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
