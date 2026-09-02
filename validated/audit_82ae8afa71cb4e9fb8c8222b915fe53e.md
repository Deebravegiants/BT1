### Title
Webhook `shop` (and other) header fields are not covered by the HMAC signature, allowing a subscriber to attribute forged webhook events to another merchant - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, then passes the `shop` (and `topic`, `webhook_id`, `api_version`) values taken directly from unauthenticated HTTP headers to the merchant-facing handler. Because the HMAC only signs the body, an attacker who legitimately receives a Shopify-signed webhook for their own shop can replay the exact same signed body while substituting the `shopify-shop-domain` header, and the gem will still accept it and hand the forged shop identity to the app's webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `shop` is read straight from the (attacker-controlled, client-supplied) HTTP header, entirely outside that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` (i.e., the raw body for webhooks) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` performs exactly this body-only HMAC check and then immediately forwards the unauthenticated `request.shop` value to the app's handler as authoritative tenant identity: [4](#0-3) 

The identity binding that should hold is: `shop-domain header used to attribute the webhook == shop-domain covered by the HMAC signature`. In this gem's implementation that equality does not hold — the HMAC binds only the body bytes, not the `shop-domain` (or `topic`/`webhook-id`) header, so the header can be swapped after Shopify signs the body without invalidating the signature check performed by this gem.

### Impact Explanation
Any internet user who can install the app on their own shop (an "unprivileged" merchant with respect to other tenants) receives genuine Shopify-signed webhooks for their own store. By replaying that same signed body to the app's webhook endpoint with the `x-shopify-shop-domain`/`shopify-shop-domain` header changed to a victim shop's domain, they cause `ShopifyAPI::Webhooks::Registry.process` to invoke the app's handler with `WebhookMetadata#shop` set to the victim's domain while the HMAC check still passes (since only the body, which is unmodified, is verified). Any handler logic that uses `data.shop` to select the tenant record/session to act on (a documented, expected usage per `docs/usage/webhooks.md`) will act under the wrong tenant's identity — a cross-tenant identity confusion rooted entirely in this gem's `Request`/`Registry`/`HmacValidator` design, not in host misuse.

### Likelihood Explanation
Exploitation only requires installing the app once (a normal, unprivileged action available to any Shopify merchant/developer) to obtain a validly HMAC-signed webhook body/signature pair, then sending an HTTP request to the app's existing public webhook endpoint with a modified shop-domain header. No access token, `client_secret`, or privileged credential is needed, and the HMAC check as implemented offers no defense against this header substitution.

### Recommendation
Bind the identity fields used by `WebhookMetadata` to the HMAC-verified payload rather than trusting unauthenticated headers. For example, incorporate the `shop`, `topic`, and `webhook_id` header values into the signable string validated by `HmacValidator`, or require host apps to cross-check `request.shop` against the shop associated with the specific `webhook_id` recorded at registration time, and document this requirement clearly for consumers of `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook with body `B`, headers including `x-shopify-shop-domain: attacker-shop.myshopify.com` and a valid `x-shopify-hmac-sha256` computed over `B` using the app's shared `api_secret_key`.
2. Capture this request. Resend it to the same app webhook endpoint, keeping body `B` and the `x-shopify-hmac-sha256` header unchanged, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`B`) only — validation succeeds because `B` and the HMAC are unmodified: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though the actual signed event originated from `attacker-shop.myshopify.com`.

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
