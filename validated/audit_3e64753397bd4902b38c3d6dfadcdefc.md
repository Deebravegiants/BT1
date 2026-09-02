### Title
Webhook shop identity (`Request#shop`) is trusted for tenant dispatch without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that `Utils::HmacValidator.validate(request)` succeeds, and that validator only signs/verifies the raw request body. The `shop` (and `topic`/`webhook-id`) values, which are taken verbatim from HTTP headers, are never included in the signed material, yet they are handed directly to the application's webhook handler as the tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly and unauthenticated from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` field, with no reference to the `shop` header at all: [3](#0-2) 

`Registry.process` accepts the request purely based on that HMAC check, then forwards `request.shop` straight into `WebhookMetadata` used by the app's handler as the tenant/shop identity: [4](#0-3) 

The equality the code implicitly assumes is: `shop_used_by_handler == shop_that_the_signature_authenticates`. In reality the signature authenticates only the body bytes; the `shop` header is parsed but never verified, so `shop_used_by_handler` can be any value an attacker chooses as long as they can present a body+HMAC pair that was legitimately signed for *some* delivery (e.g., a webhook delivered to their own installed/test shop for a topic whose body content they control or can predict, such as `app/uninstalled`, `shop/update`, or any topic with attacker-influenced body content). By replaying that legitimate `(body, hmac)` pair while swapping only the `x-shopify-shop-domain` header to a victim shop's domain, the HMAC check still passes (it never looked at the header), and the handler processes the event believing it originated from the victim tenant.

### Impact Explanation
This breaks the tenant boundary the webhook processing pipeline is supposed to enforce: an attacker who legitimately receives real webhook deliveries for their own shop (an unprivileged, self-controlled tenant) can relabel those deliveries as belonging to an arbitrary victim `shop` domain and have the host application process them as if they came from that victim. Any app logic that trusts `WebhookMetadata#shop` to select which merchant's records to look up, update, or delete (a very common pattern, e.g. `app/uninstalled` triggering data deletion, `shop/update` triggering profile changes) can be triggered against a victim tenant by an attacker who never had credentials for that tenant. This is a cross-tenant data integrity / access issue reachable by any internet-connected party who can register a test shop and receive at least one signed webhook delivery.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs a legitimately-signed `(body, hmac)` pair to replay — they cannot forge arbitrary bytes without `api_secret_key`. However, obtaining one is trivial for topics where the attacker (as their own shop's owner) controls or can predict the body content (e.g., `app/uninstalled` has a near-static/minimal body, or topics tied to attacker-editable resources), and Shopify webhook endpoints are internet-reachable by design. No privileged credentials, token theft, or social engineering is required — only the ability to install/operate the target app on a shop the attacker controls, which is normal, unprivileged usage.

### Recommendation
Bind the `shop` header (and ideally `topic`/`webhook-id`) into the value that is HMAC-verified, or independently authenticate that the `shop` header corresponds to the merchant the delivery was actually sent for (e.g., cross-check against a shop-scoped webhook secret or an out-of-band shop-to-signature association) before passing `request.shop` to handlers. At minimum, document prominently that `Utils::HmacValidator` only authenticates the body and that host applications must not treat unauthenticated header fields such as `shop` as trusted tenant identifiers without additional verification.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook delivery for a topic with attacker-controlled/predictable body, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {}
   ```
2. Attacker replays the exact same body and `x-shopify-hmac-sha256` value, but changes only the shop header:
   ```
   POST /webhooks
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <same-valid-hmac-for-body>
   x-shopify-shop-domain: victim.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {}
   ```
3. `Utils::HmacValidator.validate` recomputes HMAC over the (unchanged) body and it matches, so `Registry.process` accepts the request and dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "app/uninstalled", ...)` to the host app's handler, which then executes tenant-affecting logic against `victim.myshopify.com` on the attacker's behalf.

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
