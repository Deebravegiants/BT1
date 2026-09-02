## Title
Webhook shop-domain (and topic) header not covered by HMAC allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then trusts the `shop-domain` (and `topic`) HTTP headers unconditionally when dispatching to the registered handler. Because those headers are never included in the signed material, the identity used to authenticate the request (the app's shared secret over the body) is not bound to the identity the host application acts on (the `shop` value handed to the handler).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` values are all read straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes and compares the HMAC over `to_signable_string` (the body), never over the headers: [3](#0-2) 

`Registry.process` uses exactly this check, and once it passes, forwards `request.shop` and `request.topic` — both unauthenticated — straight to the app's handler: [4](#0-3) 

This is precisely the pattern called out in scope: "a field acted on but not covered by the HMAC." The equality that should hold is:

`shop authenticated by HMAC == shop the host app stores/acts on (request.shop)`

but in reality:

`shop authenticated by HMAC (over body bytes only) ≠ shop header value passed to WebhookMetadata`

Because the app's client secret (`Context.api_secret_key`) is shared across *all* shops that install the app, any merchant who has installed the app can capture one of their own genuine webhook deliveries (valid body + valid HMAC for that body) and replay it to the app's single shared webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header rewritten to name a different, victim shop. The HMAC check still passes because it never inspected those headers, and `Registry.process` will invoke the handler believing the data belongs to the victim shop.

### Impact Explanation
This breaks tenant isolation: an attacker who is merely one legitimate (unprivileged relative to other tenants) installer of a multi-tenant app can forge webhook events that the host application will process as if they originated from a different merchant's shop, without ever possessing that merchant's data, access token, or the app's `client_secret`. Depending on how the host app's handler uses `WebhookMetadata#shop` (e.g., to look up/update per-shop records, trigger fulfillment, or attribute billing events), this enables cross-tenant data corruption or disclosure — matching the in-scope "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on a shop they control (a normal, unprivileged action any internet user can take), capture one of their own valid webhook deliveries, and replay it to the app's public webhook callback URL with a modified `shop-domain` header. No access to `api_secret_key`, access tokens, or any other shop's credentials is needed, and no TLS interception or social engineering is required.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material inside `VerifiableQuery#to_signable_string` for webhook requests, or otherwise cryptographically bind the header values before the library considers them trustworthy in `Registry.process`. At minimum, document that `request.shop`/`request.topic` are not authenticated and must be cross-checked by the host application against its own list of known/authorized shops before use.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, which is a legitimate merchant of that app.
2. Shopify delivers a genuine webhook to the app's endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - Body: `{"id": 1, ...}` (attacker's own order data)
3. Attacker replays the exact same body and HMAC header to the same app webhook endpoint, but changes:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes HMAC over the (unchanged) body and it matches, so validation succeeds.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb`, line 190 onward) invokes the registered handler with `shop: request.shop` equal to `"victim-shop.myshopify.com"`, even though the payload never came from Shopify on behalf of that shop.

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
