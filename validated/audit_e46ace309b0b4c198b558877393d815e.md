### Title
Webhook shop identity spoofable because HMAC signs only the request body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity by validating an HMAC that covers only the raw request body, then trusts the unauthenticated `shop-domain` header to populate `WebhookMetadata#shop`, which is handed to the host application's handler as the tenant identity for the event.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC solely against that signable string [2](#0-1) . Meanwhile `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, entirely outside the HMAC's coverage [3](#0-2) . `Registry.process` validates the HMAC and, if it passes, immediately constructs `WebhookMetadata` using `request.shop` (the unauthenticated header) as the tenant identity delivered to the handler [4](#0-3) , [5](#0-4) .

This breaks the identity binding `shop authenticated by HMAC == shop acted upon by the handler`. The HMAC only proves "this body byte-sequence was signed with `client_secret`"; it says nothing about which shop the header claims to be. An attacker who can obtain any single valid `(raw_body, hmac)` pair — trivially available to any unprivileged merchant who installs the app on their own store and receives one legitimate webhook — can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header value. `HmacValidator.validate` will still pass because it never looks at the header, and the handler will receive `data.shop` set to the attacker-chosen victim shop.

### Impact Explanation
Host applications built on this gem are documented to trust `WebhookMetadata#shop` as the authenticated tenant identifier for looking up sessions, updating per-shop settings, or triggering data-deletion/redaction flows (e.g. the mandatory `shop/redact`, `customers/redact`, `customers/data_request` topics [6](#0-5) ). Because `shop` is not bound to the HMAC, an attacker can spoof events as belonging to any other merchant's shop, achieving cross-tenant action/access without ever obtaining that victim's credentials — this is a Critical-class cross-tenant impact.

### Likelihood Explanation
Medium-to-High: the attacker only needs to be an ordinary, unprivileged app-installing merchant (no `api_secret_key`, no access token, no TLS interception) to obtain one legitimate `(body, hmac)` pair from their own shop, then replay it with an edited header to the app's public webhook callback URL.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered signable string, or otherwise cryptographically bind the header value to the signed payload, so `Registry.process` cannot accept a body/HMAC pair paired with an arbitrary, attacker-chosen `shop-domain` header. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without additional verification (e.g., cross-checking against the shop associated with the resource IDs embedded in the signed body).

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook POST, capturing the raw body `B` and header `x-shopify-hmac-sha256: H` (valid for `B`).
2. Attacker sends a new POST to the same app webhook endpoint with:
   - Body: the same bytes `B`
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid for `B`)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
   - Header `x-shopify-topic`, `x-shopify-webhook-id` (freely chosen)
3. `HmacValidator.validate` computes the HMAC over `B` only [2](#0-1)  and succeeds, since it never inspects the `shop-domain` header [1](#0-0) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` [7](#0-6) , causing the host app to perform the webhook's action against the victim tenant instead of the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
