### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing via payload replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers and forwarded to the application's webhook handler. Because the HMAC verification performed by `Utils::HmacValidator.validate` only binds the *body*, the `shop` identity attached to a webhook event is never cryptographically tied to the signature that authenticates it — exactly the same class of bug as the reported `RandomizerVRF`/`RandomizerRNG` issue, where data that is "trusted" as verified is not actually included in the value that was checked.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface: [1](#0-0) [2](#0-1) 

`to_signable_string` returns `@raw_body` only. `HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` trusts `request.shop` (and `request.topic`) as authenticated once the HMAC check passes, and hands it straight to the app's handler: [4](#0-3) 

The identity binding that should hold is:

`shop_used_by_handler == shop_that_the_HMAC_actually_authenticates`

but because `shop` (and `topic`/`webhook_id`/`api_version`) are excluded from `to_signable_string`, the equality never holds — the HMAC only proves "this exact body was signed with the app secret at some point," not "this body belongs to this shop." Any party who has legitimately received one valid, signed webhook body for their *own* shop (e.g., a merchant/app-installer, who is an unprivileged actor with respect to other tenants) can replay that same body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`) header for a different shop. The signature remains valid because those headers are not part of the signed data, so the app will process/attribute the payload as belonging to the victim shop.

### Impact Explanation
This breaks the shop-tenant boundary the HMAC is supposed to enforce, i.e., cross-tenant confusion: a webhook payload cryptographically proven to originate from the app's secret can be relabeled to any shop domain and topic the attacker chooses, without needing the `api_secret_key`. Depending on how the host application keys its data/session storage off `WebhookMetadata#shop` (as the docs/tests demonstrate is the expected usage), this can let a malicious merchant inject or misattribute webhook-driven data (e.g., `app/uninstalled`, order/customer events) into another tenant's records — a cross-tenant access impact.

### Likelihood Explanation
Medium-to-High: the attacker needs one legitimately signed webhook body (trivial — every installed app receives many), and only needs to alter unauthenticated headers (`shop-domain`, `topic`, `webhook-id`) when replaying the request to the app's public webhook endpoint. No secret material, token, or privileged access is required beyond having a normal Shopify store that can install the app and observe outgoing webhooks.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the signed material, or otherwise verify them cryptographically. Concretely, since Shopify signs only the raw body by design, `Registry.process`/`Request` should not treat the header-derived `shop` as authenticated on the strength of the body HMAC alone — the host application must independently confirm the webhook's shop is one it actually installed the app for (e.g., cross-check against a known/authorized shop list or session store) before trusting `WebhookMetadata#shop`, and the gem's documentation/API should make this non-guarantee explicit so consuming apps don't assume `request.shop` is authenticated by the HMAC check.

### Proof of Concept
1. Attacker/merchant `A` installs the app on `shop-a.myshopify.com` and receives a legitimate webhook, e.g.:
   ```
   POST /webhooks
   X-Shopify-Topic: customers/update
   X-Shopify-Hmac-Sha256: <valid HMAC of body>
   X-Shopify-Shop-Domain: shop-a.myshopify.com
   Body: {"id":123,"email":"victim@example.com", ...}
   ```
2. `A` captures this exact request (valid signature over the body).
3. `A` replays the identical body/HMAC to the app's webhook endpoint, only changing the header:
   ```
   X-Shopify-Shop-Domain: shop-b.myshopify.com
   ```
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the (unchanged) body, `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) proceeds, and the handler receives `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` with `A`'s data — even though `shop-b` never sent or authorized this event.

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
